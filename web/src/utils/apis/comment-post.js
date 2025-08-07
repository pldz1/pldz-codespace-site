import { apiPost, webSitePrefix } from "./request.js";

/**
 * 获取所有评论
 * @param {string} article_id
 * @returns
 */
export async function getAllComments(article_id) {
  return apiPost(`${webSitePrefix}/comment/all`, { article_id });
}

/**
 * 添加评论
 * @param {string} article_id
 * @param {object} content
 * @param {string} parent_id
 * @returns
 */
export async function addComment(article_id, content, parent_id = "") {
  return apiPost(`${webSitePrefix}/comment/add`, { article_id, content, parent_id });
}

/**
 * 删除评论
 * @param {string} article_id
 * @param {string} comment_id
 * @returns
 */
export async function deleteComment(article_id, comment_id) {
  return apiPost(`${webSitePrefix}/comment/delete`, { article_id, comment_id });
}
