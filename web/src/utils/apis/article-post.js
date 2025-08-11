import { apiPost, webSitePrefix } from "./request.js";

/**
 * 获取文章文件内容
 * @param {*} id - 文章 ID
 * @returns {Promise<Object>}
 */
export async function getArticleText(id) {
  return apiPost(`${webSitePrefix}/article/file/text`, { id });
}

/**
 * 编辑文章内容
 * @param {string|number} articleId - 文章 ID
 * @param {Object} articleData - 文章内容数据
 * @returns {Promise<Object>}
 */
export async function editArticle(articleId, articleData) {
  return apiPost(`${webSitePrefix}/article/edit/content`, { article_id: articleId, content: articleData });
}

/**
 * 编辑文章元数据
 * @param {string|number} articleId - 文章 ID
 * @param {Object} metaData - 元数据对象
 * @returns {Promise<Object>}
 */
export async function editMeta(articleId, metaData) {
  return apiPost(`${webSitePrefix}/article/edit/meta`, { article_id: articleId, ...metaData });
}

/**
 * 更新文章的序号
 * @param {*} id
 * @param {*} serialNo
 * @returns
 */
export async function editSerialNo(id, serialNo) {
  return apiPost(`${webSitePrefix}/article/edit/serialNo`, { id, serialNo });
}

/**
 * 编辑文章标题
 * @param {*} id
 * @param {*} title
 * @returns
 */
export async function editTitle(id, title) {
  return apiPost(`${webSitePrefix}/article/edit/title`, { id, title });
}

/**
 * 添加文章分类
 * @param {*} category
 * @returns
 */
export async function addCategory(category) {
  return apiPost(`${webSitePrefix}/article/file/addcategory`, { name: category });
}

/**
 * 检查文章是否存在
 * @param {*} category
 * @param {*} title
 * @returns
 */
export async function editIsExist(category, title) {
  return apiPost(`${webSitePrefix}/article/edit/exist`, { category, title });
}

/** * 删除文章
 * @param {string|number} id - 文章 ID
 * @returns {Promise<Object>} - 返回删除结果
 */
export async function deleteArticle(id) {
  return apiPost(`${webSitePrefix}/article/file/delete`, { id });
}

/**
 * 将文章保存到缓存
 * @param {*} id
 * @returns
 */
export async function syncArticleToFile(id) {
  return apiPost(`${webSitePrefix}/article/file/sync`, { id });
}

/**
 * 重命名文章文件
 * @param {*} id
 * @param {*} filename
 * @returns
 */
export async function renameArticleFile(id, filename) {
  return apiPost(`${webSitePrefix}/article/file/rename`, { id, filename });
}

/**
 * 添加新文章
 * @param {string} category - 文章分类
 * @param {string} title - 文章标题
 * @returns {Promise<Object>} - 返回新创建的文章信息
 */
export async function addArticle(category, title) {
  return apiPost(`${webSitePrefix}/article/file/new`, { category, title });
}
