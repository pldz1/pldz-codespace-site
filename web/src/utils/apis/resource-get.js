import { apiGet, webSitePrefix } from "./request.js";

/**
 *  获取全部的在线体验的项目
 * @returns {Promise<Array>} - 返回列表
 */
export async function getAllLiveDemos() {
  return apiGet(`${webSitePrefix}/livedemo/all`);
}
