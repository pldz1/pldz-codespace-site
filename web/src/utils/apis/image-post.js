import { apiPost, webSitePrefix } from "./request.js";

/**
 * 判断图像是不是存在
 */
export async function checkImageExit(category, name) {
  return apiPost(`${webSitePrefix}/image/upload/check`, { category, name });
}

/**
 * 获取指定分类下的所有图片
 * @param {*} category
 * @returns
 */
export async function allImageInCategory(category) {
  return apiPost(`${webSitePrefix}/image/category/all`, { category });
}

/**
 * 重命名图片
 * @param {*} category
 * @param {*} oldName
 * @param {*} newName
 * @returns {Promise<Object>} - 返回重命名结果
 */
export async function renameImage(category, oldName, newName) {
  return apiPost(`${webSitePrefix}/image/rename`, { category, oldName, newName });
}

/**
 * 删除图片
 * @param {*} category
 * @param {*} name
 * @returns {Promise<Object>} - 返回删除结果
 */
export async function deleteImage(category, name) {
  return apiPost(`${webSitePrefix}/image/delete`, { category, name });
}
