import { notify } from "~/notify/notify";

const LOGIN_URL = "https://mp.weixin.qq.com/";

/**
 * 登录续期通知：session 彻底过期（cookie 也失效）时，把登录链接通知给你自己。
 *
 * 你在被 CDP 接管的那个 Chrome 里打开链接、完成登录（浏览器已记住账号，通常无需再次扫码）。
 * 登录后浏览器 cookie 是 profile 级共享的，但 session.json 里仍是旧 token——必须再跑一次
 * `refresh` 把新 token 同步进来，才能继续 pull（否则报 200040 csrf token 失效）。
 *
 * 这里只发通知、不内联轮询：登录发生在你自己的标签页，代码反复导航刷新会打断登录，
 * 交给显式的 `refresh + 重跑 pull` 更稳（update-feeds 工作流会自动编排这两步）。
 * 返回 false：本次拉取无法内联恢复，调用方据此跳过/收尾。
 */
export async function notifyRelogin(): Promise<boolean> {
  notify(
    `【wechat-feeds】微信公众号登录已过期，请在浏览器打开此链接完成登录：${LOGIN_URL} —— 登录后运行 \`bun run src/cli.ts refresh\` 同步 token 即可继续拉取。`
  );
  console.log(`  🔗 登录链接已通知：${LOGIN_URL}`);
  return false;
}
