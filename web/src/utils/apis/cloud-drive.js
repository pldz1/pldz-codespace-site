import { webSitePrefix } from "./request.js";

const prefix = `${webSitePrefix}/cloud-drive`;

async function postJson(path, body) {
  const response = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  const text = await response.text();
  let payload = null;
  if (text) {
    try {
      payload = JSON.parse(text);
    } catch (err) {
      console.error("云盘接口 JSON 解析失败:", err);
    }
  }

  if (!response.ok) {
    const detail = payload?.detail || payload?.message || `${response.status} ${response.statusText}`;
    throw new Error(detail);
  }

  return payload?.data ?? null;
}

async function getJson(path) {
  const response = await fetch(path, { method: "GET" });

  const text = await response.text();
  let payload = null;
  if (text) {
    try {
      payload = JSON.parse(text);
    } catch (err) {
      console.error("云盘接口 JSON 解析失败:", err);
    }
  }

  if (!response.ok) {
    const detail = payload?.detail || payload?.message || `${response.status} ${response.statusText}`;
    throw new Error(detail);
  }

  return payload?.data ?? null;
}

export const createDriveToken = (payload) => postJson(`${prefix}/token`, payload);

export const verifyDriveToken = (token) => postJson(`${prefix}/verify`, { token });

export const listDriveTokens = () => getJson(`${prefix}/tokens`);

export const deleteDriveToken = (token) => postJson(`${prefix}/token/delete`, { token });
