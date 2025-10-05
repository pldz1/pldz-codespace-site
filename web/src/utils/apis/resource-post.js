import { apiPost, webSitePrefix } from "./request.js";

/**
 * 设置广告位
 * @param {*} ads - 广告位数组
 * @returns {Promise<Object>} - 返回设置结果
 */
export async function setAllAdBannerItems(ads) {
  return apiPost(`${webSitePrefix}/adbanner/set`, { ads });
}

/**
 * 设置导航信息
 * @param {Array} navs - 导航信息数组，每个元素包含 { name, url, new }
 */
export async function setNavigation(navs) {
  return apiPost(`${webSitePrefix}/navs/set`, { navs });
}

/**
 * 设置代码空间导航信息
 * @param {Array} data
 */
export async function setCodeSpace(data) {
  return apiPost(`${webSitePrefix}/codespace/set`, { data });
}
