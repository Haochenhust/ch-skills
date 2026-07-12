import { existsSync, readFileSync, writeFileSync } from "fs";
import { SESSION_FILE } from "~/config";

export interface Session {
  token: string;
  loginAt: number;
}

export function getSession(): Session | null {
  if (!existsSync(SESSION_FILE)) return null;
  try {
    return JSON.parse(readFileSync(SESSION_FILE, "utf-8")) as Session;
  } catch {
    return null;
  }
}

export function saveSession(session: Session): void {
  writeFileSync(SESSION_FILE, JSON.stringify(session, null, 2));
}
