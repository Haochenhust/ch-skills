import { mkdirSync, writeFileSync, existsSync } from "fs";
import { join } from "path";
import { DATA_DIR, DEFAULT_PULL_CONCURRENCY, loadConfig } from "~/config";
import { getArticleList, fetchArticleHtml, type ArticleItem } from "~/api/mp";
import { refreshSession } from "~/auth/refresh";
import { notifyRelogin } from "~/auth/relogin";
import { htmlToMarkdown } from "~/converter/html2md";
import { getAccounts, isArticleFetched, saveArticleRecord, getArticleCount } from "~/store/db";

export interface PullOptions {
  all?: boolean;
  maxArticles?: number;
  dataDir?: string;
  date?: string;       // 指定日期，如 "2026-05-17"
  since?: string;       // 从某日期开始，如 "2026-05-01"
  today?: boolean;      // 只拉今天的
  concurrency?: number; // 同时拉取的公众号数量（默认读 config）
}

function getBeijingToday(): string {
  return new Date(Date.now() + 8 * 3600000).toISOString().slice(0, 10);
}

function getArticleDateStr(article: ArticleItem): string {
  return new Date(article.create_time * 1000 + 8 * 3600000).toISOString().slice(0, 10);
}

function matchesDateFilter(article: ArticleItem, options: PullOptions): "match" | "skip" | "stop" {
  const articleDate = getArticleDateStr(article);

  if (options.today) {
    const today = getBeijingToday();
    if (articleDate === today) return "match";
    if (articleDate < today) return "stop";
    return "skip";
  }

  if (options.date) {
    if (articleDate === options.date) return "match";
    if (articleDate < options.date) return "stop";
    return "skip";
  }

  if (options.since) {
    if (articleDate >= options.since) return "match";
    return "stop";
  }

  return "match";
}

function describeFilter(options: PullOptions): string {
  if (options.today) return `只拉今天 (${getBeijingToday()}) 的文章`;
  if (options.date) return `只拉 ${options.date} 的文章`;
  if (options.since) return `拉 ${options.since} 至今的文章`;
  return "";
}

// Session 恢复互斥锁：并发时多个账号可能同时撞到过期，这里保证 refresh/登录续期
// 全程只发生一次，其余账号共享同一次恢复结果，避免重复发送登录续期通知。
let recoveryPromise: Promise<boolean> | null = null;

function ensureRecovered(): Promise<boolean> {
  if (!recoveryPromise) {
    recoveryPromise = recoverSession();
    // 仅在成功后清空：失败结果保留，让后续账号立即拿到 false，不再重复发通知。
    recoveryPromise.then((ok) => {
      if (ok) recoveryPromise = null;
    });
  }
  return recoveryPromise;
}

async function recoverSession(): Promise<boolean> {
  console.log("  ⚠️  Session 过期，尝试自动刷新...");
  try {
    const result = await refreshSession();
    if (result.ok) {
      console.log(`  ✅ Session 已自动刷新 (新 Token: ${result.newToken})`);
      return true;
    }
    console.log("  ⚠️  刷新失败（底层登录已过期），发送登录续期通知（需登录后跑 refresh 再重跑 pull）...");
    return await notifyRelogin();
  } catch (err: any) {
    console.error(`  ❌ Session 恢复异常: ${err.message}`);
    return false;
  }
}

export async function pullAll(options: PullOptions = {}): Promise<void> {
  const accounts = getAccounts();
  if (accounts.length === 0) {
    console.log("没有订阅的公众号，请先执行 wechat-feeds add <公众号名>");
    return;
  }

  recoveryPromise = null;

  const filterDesc = describeFilter(options);
  if (filterDesc) console.log(`📅 ${filterDesc}`);

  const dataDir = options.dataDir || DATA_DIR;
  const concurrency = Math.max(
    1,
    options.concurrency ?? loadConfig().pull_concurrency ?? DEFAULT_PULL_CONCURRENCY
  );

  console.log(`🚀 并发拉取 ${accounts.length} 个公众号（并发 ${concurrency}）`);

  // 有界并发池：每个 worker 循环领取下一个账号，最多 concurrency 个账号同时进行。
  let next = 0;
  const worker = async () => {
    while (next < accounts.length) {
      const account = accounts[next++];
      await pullAccountWithRecovery(account.fakeid, account.nickname, dataDir, options);
    }
  };
  await Promise.all(
    Array.from({ length: Math.min(concurrency, accounts.length) }, worker)
  );
}

async function pullAccountWithRecovery(
  fakeid: string,
  nickname: string,
  dataDir: string,
  options: PullOptions
): Promise<void> {
  try {
    await pullAccount(fakeid, nickname, dataDir, options);
  } catch (err: any) {
    if (err.message.includes("Session 已过期")) {
      const recovered = await ensureRecovered();
      if (recovered) {
        try {
          await pullAccount(fakeid, nickname, dataDir, options);
        } catch (retryErr: any) {
          console.error(`  ❌ [${nickname}] 重试仍失败: ${retryErr.message}`);
        }
      } else {
        console.error(`  ❌ [${nickname}] Session 恢复失败，跳过`);
      }
    } else {
      console.error(`  ❌ [${nickname}] 失败: ${err.message}`);
    }
  }
}

async function pullAccount(
  fakeid: string,
  nickname: string,
  dataDir: string,
  options: PullOptions
): Promise<void> {
  const accountDir = join(dataDir, sanitizeFilename(nickname));
  mkdirSync(accountDir, { recursive: true });

  const hasDateFilter = options.today || options.date || options.since;
  const maxArticles = hasDateFilter ? 9999 : (options.maxArticles || 100);

  let begin = 0;
  let fetched = 0;
  let skipped = 0;
  let duplicated = 0;
  let shouldStop = false;

  console.log(`📥 [${nickname}] 开始`);

  while (fetched < maxArticles && !shouldStop) {
    const { articles, total, done } = await getArticleList(fakeid, begin);

    if (begin === 0) {
      const existingCount = getArticleCount(fakeid);
      console.log(`  [${nickname}] 总计 ${total} 篇，已拉取 ${existingCount} 篇`);
    }

    if (done) break;

    for (const article of articles) {
      if (fetched >= maxArticles || shouldStop) break;

      // 日期过滤
      const filterResult = matchesDateFilter(article, options);
      if (filterResult === "stop") {
        shouldStop = true;
        break;
      }
      if (filterResult === "skip") continue;

      const articleId = `${fakeid}:${article.aid}`;

      // 去重：已拉取过的跳过
      if (isArticleFetched(articleId)) {
        duplicated++;
        continue;
      }

      // 文件级去重：同名文件已存在也跳过
      const dateStr = getArticleDateStr(article);
      const filename = `${dateStr}-${sanitizeFilename(article.title)}.md`;
      const filePath = join(accountDir, filename);
      if (existsSync(filePath)) {
        duplicated++;
        continue;
      }

      try {
        await fetchAndSave(article, fakeid, nickname, accountDir);
        fetched++;
        console.log(`  ✅ [${nickname}] [${fetched}] ${article.title}`);
      } catch (err: any) {
        console.error(`  ⚠️  [${nickname}] 跳过: ${article.title} (${err.message})`);
        skipped++;
      }

      await sleep(1000);
    }

    begin += articles.length;
    await sleep(2000);
  }

  if (duplicated > 0) {
    console.log(`✅ [${nickname}] 完成: 新增 ${fetched} 篇, 跳过 ${skipped} 篇, 重复 ${duplicated} 篇`);
  } else {
    console.log(`✅ [${nickname}] 完成: 新增 ${fetched} 篇, 跳过 ${skipped} 篇`);
  }
}

async function fetchAndSave(
  article: ArticleItem,
  fakeid: string,
  nickname: string,
  accountDir: string
): Promise<void> {
  const html = await fetchArticleHtml(article.link);

  const dateStr = getArticleDateStr(article);
  const slug = `${dateStr}-${sanitizeFilename(article.title)}`;

  // 当前只保存纯文本，图片保留原 CDN URL（不下载到本地）。
  // 想本地化图片：用 converter/images.ts 的 downloadArticleImages 拿到 urlToLocal，传入下面第三个参数。
  const markdown = htmlToMarkdown(html, {
    title: article.title,
    author: nickname,
    date: dateStr,
    url: article.link,
    digest: article.digest,
  });

  const filename = `${slug}.md`;
  const filePath = join(accountDir, filename);
  writeFileSync(filePath, markdown, "utf-8");

  saveArticleRecord({
    id: `${fakeid}:${article.aid}`,
    fakeid,
    title: article.title,
    url: article.link,
    author: article.author_name || nickname,
    publishTime: article.create_time,
    filePath,
  });
}

function sanitizeFilename(name: string): string {
  return name.replace(/[\/\\:*?"<>|]/g, "_").slice(0, 80);
}

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}
