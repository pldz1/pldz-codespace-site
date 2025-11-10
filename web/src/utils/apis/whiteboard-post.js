import { apiPost, webSitePrefix } from "./request.js";

/**
 * 获取白板内容
 * @param {*} key
 * @returns
 */
export async function getWhiteBoardByKey(key) {
  return apiPost(`${webSitePrefix}/whiteboard/key`, { key });
}

/**
 * 获取指定用户的白板内容列表
 * @returns
 */
export async function getWhiteBoardByUser(username = "", createNew = true) {
  return apiPost(`${webSitePrefix}/whiteboard/authorized`, {
    username,
    create_new: createNew,
  });
}

/**
 * 更新白板内容
 * @param {*} key
 * @param {*} content
 * @returns
 */
export async function updateWhiteBoardContent(key, content) {
  return apiPost(`${webSitePrefix}/whiteboard/update`, { key, content });
}
