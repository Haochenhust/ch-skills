import { mpRequest, findLiveMpTarget } from "./request";
import { CDP_PROXY_URL as CDP_PROXY } from "~/config";

export interface AccountInfo {
  fakeid: string;
  nickname: string;
  alias: string;
  round_head_img: string;
  service_type: number;
}

export interface ArticleItem {
  aid: string;
  title: string;
  link: string;
  digest: string;
  cover: string;
  create_time: number;
  update_time: number;
  author_name: string;
  item_show_type: number;
}

interface SearchBizResponse {
  base_resp: { ret: number; err_msg: string };
  list: AccountInfo[];
  total: number;
}

interface AppMsgPublishResponse {
  base_resp: { ret: number; err_msg: string };
  publish_page: string;
}

interface PublishPage {
  publish_list: Array<{ publish_info: string }>;
  total_count: number;
}

interface PublishInfo {
  appmsgex: ArticleItem[];
}

export async function searchAccount(keyword: string): Promise<AccountInfo[]> {
  const resp = await mpRequest<SearchBizResponse>({
    endpoint: "/cgi-bin/searchbiz",
    query: {
      action: "search_biz",
      begin: 0,
      count: 5,
      query: keyword,
    },
  });

  if (resp.base_resp.ret === 0) {
    return resp.list;
  } else if (resp.base_resp.ret === 200003 || resp.base_resp.ret === 200040) {
    // 200003=session 过期；200040=csrf token 失效（重新登录后旧 token 未同步）。
    // 两者都能靠 refreshSession 重取 token 自愈，归入同一恢复分支触发自动刷新。
    throw new Error("Session 已过期，请重新执行 wechat-feeds login");
  }
  throw new Error(`搜索公众号失败: ${resp.base_resp.ret} ${resp.base_resp.err_msg}`);
}

export async function getArticleList(
  fakeid: string,
  begin = 0,
  count = 20
): Promise<{ articles: ArticleItem[]; total: number; done: boolean }> {
  const resp = await mpRequest<AppMsgPublishResponse>({
    endpoint: "/cgi-bin/appmsgpublish",
    query: {
      sub: "list",
      search_field: "null",
      begin,
      count,
      fakeid,
      type: "101_1",
      free_publish_type: 1,
      sub_action: "list_ex",
    },
  });

  if (resp.base_resp.ret === 0) {
    const page: PublishPage = JSON.parse(resp.publish_page);
    const publishList = page.publish_list.filter((item) => !!item.publish_info);
    const done = publishList.length === 0;

    const articles = publishList.flatMap((item) => {
      const info: PublishInfo = JSON.parse(item.publish_info);
      return info.appmsgex;
    });

    return { articles, total: page.total_count, done };
  } else if (resp.base_resp.ret === 200003 || resp.base_resp.ret === 200040) {
    // 200003=session 过期；200040=csrf token 失效（重新登录后旧 token 未同步）。
    // 两者都能靠 refreshSession 重取 token 自愈，归入同一恢复分支触发自动刷新。
    throw new Error("Session 已过期，请重新执行 wechat-feeds login");
  }
  throw new Error(`获取文章列表失败: ${resp.base_resp.ret} ${resp.base_resp.err_msg}`);
}

async function getMpTargetId(): Promise<string> {
  const live = await findLiveMpTarget();
  if (!live) throw new Error("未找到可用的微信公众号页面（mp 标签页不存在或均无响应）");
  return live;
}

export async function fetchArticleHtml(url: string): Promise<string> {
  const targetId = await getMpTargetId();

  // 在公众号后台页面内用 fetch 拉取文章 HTML（同源请求，自带 cookie，不触发反爬）
  const js = `
    (async () => {
      try {
        const resp = await fetch("${url.replace(/"/g, '\\"')}", {
          credentials: "include",
          headers: { "Accept": "text/html" }
        });
        if (!resp.ok) return JSON.stringify({error: "HTTP " + resp.status});
        const html = await resp.text();

        // 检查文章状态
        if (html.includes("已被发布者删除") || html.includes("此内容已被删除")) {
          return JSON.stringify({error: "deleted"});
        }
        if (html.includes("环境异常") || html.includes("verify_container")) {
          return JSON.stringify({error: "anti-crawl"});
        }
        if (html.includes("此内容因违规无法查看") || html.includes("被投诉且经审核涉嫌侵权")) {
          return JSON.stringify({error: "removed"});
        }

        // 用 DOMParser 提取正文
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, "text/html");
        const content = doc.querySelector("#js_content") || doc.querySelector(".rich_media_content");
        if (content) {
          // 过滤掉内容过短的（可能是异常页面）
          const text = content.textContent?.trim() || "";
          if (text.length < 20) {
            return JSON.stringify({error: "empty", hint: text.substring(0, 100)});
          }
          return JSON.stringify({html: content.innerHTML});
        }

        // fallback: 返回 body
        return JSON.stringify({html: doc.body?.innerHTML || "", fallback: true});
      } catch(e) {
        return JSON.stringify({error: e.message});
      }
    })()
  `;

  const evalResp = await fetch(`${CDP_PROXY}/eval?target=${targetId}`, {
    method: "POST",
    body: js,
  });
  const evalResult = await evalResp.json();

  if (evalResult.error) {
    throw new Error(`CDP eval 失败: ${evalResult.error}`);
  }

  const result = JSON.parse(evalResult.value);

  if (result.error === "deleted") {
    throw new Error("文章已被作者删除");
  }
  if (result.error === "removed") {
    throw new Error("文章因违规已被移除");
  }
  if (result.error === "anti-crawl") {
    throw new Error("文章内容被反爬拦截");
  }
  if (result.error === "empty") {
    throw new Error(`文章内容为空: ${result.hint || ""}`);
  }
  if (result.error) {
    throw new Error(`获取文章失败: ${result.error}`);
  }

  return `<div id="js_content">${result.html}</div>`;
}

export async function getAccountFromArticleUrl(url: string): Promise<string> {
  const targetId = await getMpTargetId();

  const js = `
    (async () => {
      try {
        const resp = await fetch("${url.replace(/"/g, '\\"')}", {
          credentials: "include",
          headers: { "Accept": "text/html" }
        });
        const html = await resp.text();
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, "text/html");

        // #js_name 是公众号名称（不是文章作者）
        const nickname = doc.querySelector("#js_name")?.textContent?.trim()
          || doc.querySelector("a.rich_media_meta_nickname")?.textContent?.trim()
          || "";

        return JSON.stringify({ nickname });
      } catch(e) {
        return JSON.stringify({ error: e.message });
      }
    })()
  `;

  const evalResp = await fetch(`${CDP_PROXY}/eval?target=${targetId}`, {
    method: "POST",
    body: js,
  });
  const evalResult = await evalResp.json();
  if (evalResult.error) throw new Error(`CDP eval 失败: ${evalResult.error}`);

  const result = JSON.parse(evalResult.value);
  if (result.error) throw new Error(`提取公众号失败: ${result.error}`);
  if (!result.nickname) throw new Error("无法从文章中提取公众号名称");

  return result.nickname;
}
