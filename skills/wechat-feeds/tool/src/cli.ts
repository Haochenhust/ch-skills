#!/usr/bin/env bun

import { startLogin } from "./auth/login";
import { refreshSession } from "./auth/refresh";
import { notifyRelogin } from "./auth/relogin";
import { getSession } from "./auth/session";
import { searchAccount, getAccountFromArticleUrl } from "./api/mp";
import { ensureCdpReady } from "./api/request";
import { addAccount, getAccounts, getArticleCount } from "./store/db";
import { pullAll } from "./fetcher/pull";

const args = process.argv.slice(2);
const command = args[0];

async function main() {
  switch (command) {
    case "login":
      await startLogin();
      break;

    case "add":
      await handleAdd(args[1]);
      break;

    case "pull":
      await handlePull();
      break;

    case "refresh":
      await handleRefresh();
      break;

    case "relogin":
      await notifyRelogin();
      break;

    case "keepalive":
      await handleKeepalive();
      break;

    case "status":
      handleStatus();
      break;

    case "list":
      handleList();
      break;

    default:
      printUsage();
  }
}

async function handleAdd(input?: string) {
  if (!input) {
    console.log("用法:\n  wechat-feeds add <公众号名称>\n  wechat-feeds add <文章链接>");
    return;
  }

  checkSession();

  let keyword = input;

  // 如果输入是 URL，先从文章中提取公众号名称
  if (input.startsWith("http")) {
    console.log(`🔗 从文章链接提取公众号...`);
    keyword = await getAccountFromArticleUrl(input);
    console.log(`  公众号: ${keyword}`);
  }

  console.log(`🔍 搜索: ${keyword}`);
  const accounts = await searchAccount(keyword);

  if (accounts.length === 0) {
    console.log("未找到匹配的公众号");
    return;
  }

  // 取第一个结果
  const account = accounts[0];
  addAccount(account.fakeid, account.nickname, account.alias);
  console.log(`✅ 已添加: ${account.nickname} (${account.alias || account.fakeid})`);
}

async function handlePull() {
  checkSession();

  const allFlag = args.includes("--all");
  const todayFlag = args.includes("--today");
  const maxStr = args.find((a) => a.startsWith("--max="));
  const dateStr = args.find((a) => a.startsWith("--date="));
  const sinceStr = args.find((a) => a.startsWith("--since="));
  const concStr = args.find((a) => a.startsWith("--concurrency="));

  await pullAll({
    all: allFlag,
    today: todayFlag,
    date: dateStr?.split("=")[1],
    since: sinceStr?.split("=")[1],
    maxArticles: maxStr ? parseInt(maxStr.split("=")[1]) : undefined,
    concurrency: concStr ? parseInt(concStr.split("=")[1]) : undefined,
  });

  console.log("\n✨ 拉取完成");
}

function handleStatus() {
  const session = getSession();
  if (!session) {
    console.log("❌ 未登录");
    return;
  }

  const loginAt = new Date(session.loginAt).toLocaleString("zh-CN");
  const daysSinceLogin = ((Date.now() - session.loginAt) / 86400000).toFixed(1);

  console.log("📊 状态:");
  console.log(`  登录时间: ${loginAt} (${daysSinceLogin} 天前)`);
  console.log(`  Token: ${session.token}`);

  const accounts = getAccounts();
  console.log(`\n  订阅公众号: ${accounts.length} 个`);
}

function handleList() {
  const accounts = getAccounts();
  if (accounts.length === 0) {
    console.log("暂无订阅的公众号");
    return;
  }

  console.log("📋 订阅列表:\n");
  for (const acc of accounts) {
    const count = getArticleCount(acc.fakeid);
    console.log(`  ${acc.nickname} (${acc.alias || acc.fakeid}) — ${count} 篇`);
  }
}

async function handleRefresh() {
  checkSession();
  console.log("🔄 正在刷新 session...");
  const result = await refreshSession();
  if (result.ok) {
    console.log(`✅ 刷新成功！新 Token: ${result.newToken}`);
  } else {
    console.log("❌ 刷新失败，session 已过期，需要重新登录续期（relogin 会发登录续期通知）");
  }
}

// 每日保活（定时任务调用，如 cron / launchd）：refresh 成功则静默续命 cookie；
// cookie 已死则发登录续期通知，把登录变成可预期动作而非拉取中途的阻塞。
// CDP/Chrome 没起时直接跳过（不算失败），等下一次调度。
async function handleKeepalive() {
  const ts = new Date().toLocaleString("zh-CN", { timeZone: "Asia/Shanghai" });

  try {
    await ensureCdpReady();
  } catch {
    console.log(`[${ts}] ⏭️  CDP proxy 未运行，跳过本次保活`);
    return;
  }

  if (!getSession()) {
    console.log(`[${ts}] ⏭️  未登录（无 session.json），跳过本次保活`);
    return;
  }

  const result = await refreshSession();
  if (result.ok) {
    console.log(`[${ts}] ✅ 保活成功，token: ${result.newToken}`);
    return;
  }

  console.log(`[${ts}] ⚠️  cookie 已失效，发送登录续期通知...`);
  await notifyRelogin();
  console.log(`[${ts}] 🔗 已发送登录链接，登录后下次保活会自动同步 token`);
}

function checkSession() {
  const session = getSession();
  if (!session) {
    console.error("❌ 未登录，请先执行: bun run src/cli.ts login");
    process.exit(1);
  }
}

function printUsage() {
  console.log(`
wechat-feeds — 微信公众号文章拉取工具

用法:
  bun run src/cli.ts login            扫码登录微信公众号平台
  bun run src/cli.ts add <名称>       添加要订阅的公众号
  bun run src/cli.ts list             查看订阅列表
  bun run src/cli.ts refresh            主动刷新 session
  bun run src/cli.ts relogin            登录彻底过期时发登录续期通知（登录后跑 refresh 同步）
  bun run src/cli.ts keepalive          每日保活（定时任务调用）：刷新 cookie，失效则发登录续期通知
  bun run src/cli.ts pull              拉取新文章（默认最多100篇）
  bun run src/cli.ts pull --today      只拉今天发的文章
  bun run src/cli.ts pull --date=MM-DD 拉指定日期的文章
  bun run src/cli.ts pull --since=MM-DD 拉某日期至今的所有文章
  bun run src/cli.ts pull --max=50     限制每个公众号最多拉取N篇
  bun run src/cli.ts pull --concurrency=6  同时拉取的公众号数量（默认4，越大越快但更易触发频控）
  bun run src/cli.ts status            查看登录状态
`);
}

main().catch((err) => {
  console.error(`\n💥 错误: ${err.message}`);
  process.exit(1);
});
