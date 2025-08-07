import { apiGet, webSitePrefix } from "./request.js";

/**
 *  获取全部的代码空间项目
 * @returns {Promise<Array>} - 返回代码空间项目列表
 */
export async function getAllAdBannerItem() {
  return apiGet(`${webSitePrefix}/adbanner/all`);
}

/**
 * 获取导航信息
 * @returns {Promise<Array>} - 返回导航信息列表
 */
export async function getNavigation() {
  return apiGet(`${webSitePrefix}/navs/all`);
}
