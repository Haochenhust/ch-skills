import { getSession, saveSession } from "./session";
import { findLiveMpTarget } from "~/api/request";
import { CDP_PROXY_URL as CDP_PROXY } from "~/config";

/**
 * 主动刷新 session：让浏览器重新访问公众号后台首页。
 * 如果 cookie 仍有效，浏览器会自动登录（不需要扫码），触发完整的 session 刷新。
 * 如果 cookie 已过期，会跳到登录页——此时返回 false，需要重新登录续期。
 */
export async function refreshSession(): Promise<{ ok: boolean; newToken?: string }> {
  const session = getSession();
  if (!session) return { ok: false };

  // 找到已有的活 MP 标签页（跳过被冻结的僵尸 tab），没有则新建
  const mpTargetId = await findLiveMpTarget();

  let targetId: string;

  if (mpTargetId) {
    targetId = mpTargetId;
    // 导航到公众号后台首页（触发浏览器的完整 cookie 交换）
    await fetch(`${CDP_PROXY}/navigate?target=${targetId}&url=https://mp.weixin.qq.com/`);
  } else {
    // 新开一个 tab 访问公众号首页
    const newTab = await fetch(`${CDP_PROXY}/new?url=https://mp.weixin.qq.com/`).then(r => r.json());
    targetId = newTab.targetId;
  }

  await sleep(5000);

  // 检查跳转结果
  const evalResp = await fetch(`${CDP_PROXY}/eval?target=${targetId}`, {
    method: "POST",
    body: "window.location.href",
  });
  const result = await evalResp.json();
  const currentUrl = result.value || "";

  // 如果 URL 包含 token，说明自动登录成功
  if (currentUrl.includes("token=")) {
    const newToken = new URL(currentUrl).searchParams.get("token");
    if (newToken) {
      saveSession({ token: newToken, loginAt: Date.now() });
      return { ok: true, newToken };
    }
  }

  // 如果停在首页（登录页），说明 cookie 已过期
  if (currentUrl === "https://mp.weixin.qq.com/" || currentUrl.includes("loginpage")) {
    return { ok: false };
  }

  // 可能需要更多时间加载，再等一轮
  await sleep(3000);
  const retryResp = await fetch(`${CDP_PROXY}/eval?target=${targetId}`, {
    method: "POST",
    body: "window.location.href",
  });
  const retryResult = await retryResp.json();
  const retryUrl = retryResult.value || "";

  if (retryUrl.includes("token=")) {
    const newToken = new URL(retryUrl).searchParams.get("token");
    if (newToken) {
      saveSession({ token: newToken, loginAt: Date.now() });
      return { ok: true, newToken };
    }
  }

  return { ok: false };
}

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}
