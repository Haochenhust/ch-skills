import { getSession } from "~/auth/session";
import { CDP_PROXY_URL as CDP_PROXY } from "~/config";

export interface MpRequestOptions {
  endpoint: string;
  query?: Record<string, string | number>;
  method?: "GET" | "POST";
  body?: Record<string, string | number>;
  injectToken?: boolean;
}

let cachedTargetId: string | null = null;

// 探测标签页能否响应 JS 执行。被 Chrome 内存节省机制冻结/丢弃的僵尸 tab
// 仍出现在 /targets 列表里，但对 Runtime.evaluate 永久无响应（只能等到超时）。
export async function isTabResponsive(targetId: string, timeoutMs = 2500): Promise<boolean> {
  try {
    const resp = await fetch(`${CDP_PROXY}/eval?target=${targetId}`, {
      method: "POST",
      body: "1",
      signal: AbortSignal.timeout(timeoutMs),
    });
    const result = await resp.json();
    return !result.error;
  } catch {
    return false;
  }
}

// 依次探测所有 mp.weixin.qq.com 标签页，返回第一个活的；全是僵尸则返回 null。
export async function findLiveMpTarget(): Promise<string | null> {
  const targets = await fetch(`${CDP_PROXY}/targets`).then((r) => r.json());
  const candidates = targets.filter((t: any) => t.url?.includes("mp.weixin.qq.com"));
  for (const t of candidates) {
    if (await isTabResponsive(t.targetId)) return t.targetId;
  }
  return null;
}

async function getTargetId(): Promise<string> {
  if (cachedTargetId) {
    const info = await fetch(`${CDP_PROXY}/info?target=${cachedTargetId}`).then(r => r.json()).catch(() => null);
    if (info?.url?.includes("mp.weixin.qq.com")) return cachedTargetId;
    cachedTargetId = null;
  }

  const live = await findLiveMpTarget();
  if (live) {
    cachedTargetId = live;
    return live;
  }

  throw new Error(
    "未找到可用的微信公众号页面（mp 标签页不存在或均无响应）。请先执行 wechat-feeds login，或在 Chrome 中重新打开 mp.weixin.qq.com"
  );
}

export async function mpRequest<T = any>(options: MpRequestOptions): Promise<T> {
  const session = getSession();
  if (!session) throw new Error("未登录，请先执行 wechat-feeds login");

  const targetId = await getTargetId();

  const query: Record<string, string | number> = { ...options.query };
  if (options.injectToken !== false) {
    query.token = session.token;
    query.lang = "zh_CN";
    query.f = "json";
    query.ajax = 1;
  }

  const qs = new URLSearchParams(query as Record<string, string>).toString();
  const url = `${options.endpoint}${qs ? "?" + qs : ""}`;

  const js = `
    (async () => {
      const resp = await fetch("${url}", {
        method: "${options.method || "GET"}",
        credentials: "include"
        ${options.method === "POST" && options.body
          ? `, headers: {"Content-Type": "application/x-www-form-urlencoded"}, body: "${new URLSearchParams(options.body as Record<string, string>).toString()}"`
          : ""}
      });
      return await resp.text();
    })()
  `;

  const evalResp = await fetch(`${CDP_PROXY}/eval?target=${targetId}`, {
    method: "POST",
    body: js,
  });

  const evalResult = await evalResp.json();

  if (evalResult.error) {
    // 超时大概率是 tab 在请求间隙被冻结了，清掉缓存让下次重新探测选活 tab
    if (String(evalResult.error).includes("超时")) cachedTargetId = null;
    throw new Error(`CDP eval error: ${evalResult.error}`);
  }

  try {
    return JSON.parse(evalResult.value) as T;
  } catch {
    throw new Error(`Invalid JSON response: ${evalResult.value?.substring(0, 200)}`);
  }
}

export async function ensureCdpReady(): Promise<void> {
  try {
    await fetch(`${CDP_PROXY}/targets`);
  } catch {
    throw new Error("CDP Proxy 未运行。请先启动 Chrome（开启远程调试）并运行 cdp-proxy.mjs。");
  }
}
