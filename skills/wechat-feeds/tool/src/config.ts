import { join, dirname } from "path";
import { existsSync, readFileSync } from "fs";

// 项目根目录（cli.ts 的父目录）
export const ROOT_DIR = join(dirname(new URL(import.meta.url).pathname), "..");

export const SESSION_FILE = join(ROOT_DIR, "session.json");
export const DB_PATH = join(ROOT_DIR, "feeds.db");
// 文章落地目录（项目内）：data/<公众号昵称>/<YYYY-MM-DD>-<标题>.md
export const DATA_DIR = join(ROOT_DIR, "data");
export const CONFIG_FILE = join(ROOT_DIR, "config.json");

// CDP proxy 地址：抓取全程通过它操控本机 Chrome（见根目录 cdp-proxy.mjs）。
// 端口默认 3456，可用环境变量 WECHAT_FEEDS_CDP_URL 覆盖。
export const CDP_PROXY_URL =
  process.env.WECHAT_FEEDS_CDP_URL || "http://localhost:3456";

// 登录过期通知：session 彻底失效时，把登录链接交给这条命令通知你自己
// （飞书 / Slack / 邮件 / 桌面通知都行）。消息通过 stdin 和环境变量
// WECHAT_FEEDS_MSG 一并传入；未设置时退化为仅打印到控制台。
// 例：export WECHAT_FEEDS_NOTIFY_CMD='osascript -e "display notification \"$WECHAT_FEEDS_MSG\""'
export const NOTIFY_CMD = process.env.WECHAT_FEEDS_NOTIFY_CMD || "";

export interface FeedsConfig {
  accounts: string[];
  pull_interval_hours: number;
  data_dir: string;
  max_articles_per_pull: number;
  pull_concurrency: number;
}

// 同时拉取的公众号数量。账号内部仍顺序+限速，总请求速率 ≈ 并发数 × 单账号速率。
// 默认偏保守：微信 appmsgpublish 接口有频控，并发过高可能触发风控。
export const DEFAULT_PULL_CONCURRENCY = 4;

export function loadConfig(): FeedsConfig {
  if (!existsSync(CONFIG_FILE)) {
    return {
      accounts: [],
      pull_interval_hours: 24,
      data_dir: "./data",
      max_articles_per_pull: 100,
      pull_concurrency: DEFAULT_PULL_CONCURRENCY,
    };
  }
  const cfg = JSON.parse(readFileSync(CONFIG_FILE, "utf-8"));
  return { pull_concurrency: DEFAULT_PULL_CONCURRENCY, ...cfg };
}
