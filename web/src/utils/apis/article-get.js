import { apiGet, webSitePrefix } from "./request.js";

/**
 * 获取所有文章
 * @returns {Promise<Array>}
 */
export async function getAllArticles() {
  return apiGet(`${webSitePrefix}/article/all/article`);
}

/**
 * 获取全部的分类信息
 * @returns {Promise<Array>}
 */
export async function getAllCategories() {
  return apiGet(`${webSitePrefix}/article/all/category`);
}

/**
 * 获取全部的tag的统计数据
 * @returns {Promise<Array>}
 */
export async function getTagCounts() {
  return apiGet(`${webSitePrefix}/article/all/tag`);
}

/**
 * 根据分类 ID 获取文章列表
 * @param {string|number} categoryId - 分类 ID
 * @returns {Promise<Array>}
 */
export async function getArticlesByCategory(categoryId) {
  return apiGet(`${webSitePrefix}/article/category/${categoryId}`);
}

/**
 * 根据 ID 获取单篇文章
 * @param {string|number} articleId - 文章 ID
 * @returns {Promise<Object>}
 */
export async function getArticle(articleId) {
  return apiGet(`${webSitePrefix}/article/id/${articleId}`);
}

/**
 * 根据标签获取相关文章
 * @param {string} tag - 标签名称
 * @returns {Promise<Array>} - 相关文章列表
 */
export async function getArticlesByTag(tag) {
  return apiGet(`${webSitePrefix}/article/tag/${tag}`);
}
