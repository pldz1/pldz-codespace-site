import { apiGet, apiPost, hostPrefix } from "./request.js";

/**
 * 获取所有缓存数据
 * @returns {Promise<Array>} - 返回所有缓存数据
 */
export async function getAllCache() {
  return apiGet(`${hostPrefix}/resource/cache/all`);
}

/**
 * 下载缓存文件
 * @param {*} filename
 * @returns
 */
export async function downloadCacheFile(filename) {
  return apiPost(`${hostPrefix}/resource/cache/download`, { filename }, true);
}

/**
 * 删除缓存文件
 * @param {*} filename
 * @returns
 */
export async function deleteCacheFile(filename) {
  return apiPost(`${hostPrefix}/resource/cache/delete`, { filename });
}
