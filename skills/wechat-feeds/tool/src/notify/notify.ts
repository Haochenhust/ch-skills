import { spawnSync } from "child_process";
import { NOTIFY_CMD } from "~/config";

/**
 * 通用通知：把一条文本消息交给用户配置的命令 (WECHAT_FEEDS_NOTIFY_CMD) 发出去。
 * 消息同时通过 stdin 和环境变量 WECHAT_FEEDS_MSG 传入，命令里两种取法都行。
 * 未配置命令时退化为打印到控制台（登录续期这类消息本就会出现在 pull 输出里）。
 *
 * 例（飞书，用你自己的 lark-cli / webhook 包一层）：
 *   export WECHAT_FEEDS_NOTIFY_CMD='curl -s -X POST "$MY_FEISHU_WEBHOOK" -d "{\"msg_type\":\"text\",\"content\":{\"text\":\"$WECHAT_FEEDS_MSG\"}}"'
 * 例（macOS 桌面通知）：
 *   export WECHAT_FEEDS_NOTIFY_CMD='osascript -e "display notification \"$WECHAT_FEEDS_MSG\""'
 */
export function notify(text: string): boolean {
  if (!NOTIFY_CMD) {
    console.log(`  🔔 ${text}`);
    return true;
  }
  const result = spawnSync("sh", ["-c", NOTIFY_CMD], {
    input: text,
    env: { ...process.env, WECHAT_FEEDS_MSG: text },
    encoding: "utf-8",
  });
  if (result.status !== 0) {
    console.error(`  ⚠️ 通知命令失败: ${(result.stderr || "").slice(0, 200)}`);
    return false;
  }
  return true;
}
