import { Database } from "bun:sqlite";
import { DB_PATH } from "~/config";

let db: Database | null = null;

export function getDb(): Database {
  if (!db) {
    db = new Database(DB_PATH);
    db.exec("PRAGMA journal_mode = WAL");
    initSchema(db);
  }
  return db;
}

function initSchema(db: Database): void {
  db.exec(`
    CREATE TABLE IF NOT EXISTS accounts (
      fakeid TEXT PRIMARY KEY,
      nickname TEXT NOT NULL,
      alias TEXT,
      added_at INTEGER NOT NULL
    );

    CREATE TABLE IF NOT EXISTS articles (
      id TEXT PRIMARY KEY,
      fakeid TEXT NOT NULL,
      title TEXT NOT NULL,
      url TEXT NOT NULL,
      author TEXT,
      publish_time INTEGER NOT NULL,
      fetched_at INTEGER,
      file_path TEXT,
      FOREIGN KEY (fakeid) REFERENCES accounts(fakeid)
    );

    CREATE INDEX IF NOT EXISTS idx_articles_fakeid ON articles(fakeid);
    CREATE INDEX IF NOT EXISTS idx_articles_publish_time ON articles(publish_time);
  `);
}

export function isArticleFetched(articleId: string): boolean {
  const row = getDb()
    .prepare("SELECT 1 FROM articles WHERE id = ? AND fetched_at IS NOT NULL")
    .get(articleId);
  return !!row;
}

export function saveArticleRecord(article: {
  id: string;
  fakeid: string;
  title: string;
  url: string;
  author: string;
  publishTime: number;
  filePath: string;
}): void {
  getDb()
    .prepare(
      `INSERT OR REPLACE INTO articles (id, fakeid, title, url, author, publish_time, fetched_at, file_path)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?)`
    )
    .run(
      article.id,
      article.fakeid,
      article.title,
      article.url,
      article.author,
      article.publishTime,
      Date.now(),
      article.filePath
    );
}

export function addAccount(fakeid: string, nickname: string, alias: string): void {
  getDb()
    .prepare(
      "INSERT OR IGNORE INTO accounts (fakeid, nickname, alias, added_at) VALUES (?, ?, ?, ?)"
    )
    .run(fakeid, nickname, alias, Date.now());
}

export function getAccounts(): Array<{ fakeid: string; nickname: string; alias: string }> {
  return getDb().prepare("SELECT fakeid, nickname, alias FROM accounts").all() as any[];
}

export function getArticleCount(fakeid: string): number {
  const row = getDb()
    .prepare("SELECT COUNT(*) as count FROM articles WHERE fakeid = ? AND fetched_at IS NOT NULL")
    .get(fakeid) as any;
  return row?.count || 0;
}
