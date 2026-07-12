import { saveSession } from "./session";
import { CDP_PROXY_URL as CDP_PROXY } from "~/config";

export async function startLogin(): Promise<void> {
  console.log("🔐 开始登录微信公众号平台...\n");

  // 检查 CDP Proxy
  try {
    await fetch(`${CDP_PROXY}/targets`);
  } catch {
    throw new Error("CDP Proxy 未运行。请确保 Chrome 已开启远程调试，且 cdp-proxy.mjs 已启动。");
  }

  // 打开微信公众号登录页
  const newTab = await fetch(`${CDP_PROXY}/new?url=https://mp.weixin.qq.com/`).then(r => r.json());
  const targetId = newTab.targetId;
  console.log("📱 已打开微信公众号登录页，请用微信扫码登录\n");

  // 轮询等待登录成功（页面跳转到含 token 的 URL）
  console.log("⏳ 等待扫码...");
  for (let i = 0; i < 120; i++) {
    await sleep(3000);

    try {
      const evalResp = await fetch(`${CDP_PROXY}/eval?target=${targetId}`, {
        method: "POST",
        body: "window.location.href",
      });
      const result = await evalResp.json();
      const url = result.value;

      if (url && url.includes("token=")) {
        const token = new URL(url).searchParams.get("token");
        if (token) {
          saveSession({ token, loginAt: Date.now() });
          console.log(`\n🎉 登录成功！Token: ${token}`);
          console.log("   Session 已保存，可以开始拉取文章了。\n");
          console.log("   ⚠️  请保持此 Chrome 标签页打开（可最小化），API 调用依赖浏览器 session。\n");
          return;
        }
      }

      if (i % 5 === 0 && i > 0) {
        process.stdout.write(".");
      }
    } catch {
      // CDP 连接暂时失败，继续重试
    }
  }

  // 超时，清理
  try {
    await fetch(`${CDP_PROXY}/close?target=${targetId}`);
  } catch {}

  throw new Error("登录超时，请重新执行 login");
}

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}
