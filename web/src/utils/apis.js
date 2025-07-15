/**
 * 通用 API 请求函数，自动处理请求、响应与错误
 * @param {string} path - 请求路径，例如 '/api/v1/website/articles/all'
 * @param {Object} [options] - Fetch 配置项
 * @param {boolean} [isBlob=false] - 是否处理为 Blob 对象
 * @returns {Promise<any>} - 返回后端返回的数据部分
 * @throws {Error} - 网络错误或 JSON 解析错误
 */
async function apiRequest(path, options = {}, isBlob = false) {
  const response = await fetch(path, options);
  if (!response.ok) {
    console.error(`网络响应失败 (${response.status} ${response.statusText})`);
    return null;
  }

  let payload;
  try {
    if (isBlob) {
      // 如果需要处理为 Blob 对象，直接返回 Blob
      payload = await response.blob();
      return payload;
    }
    payload = await response.json();
  } catch (err) {
    console.error(`JSON 解析失败: ${err.message}`);
    return null;
  }

  // 假设后端返回格式为 { data: ... }
  return payload.data;
}

/**
 * 发送 GET 请求
 * @param {string} path - 请求路径
 * @returns {Promise<any>}
 */
export const apiGet = (path) => apiRequest(path);

/**
 * 发送 POST 请求，自动设置 Content-Type 为 JSON
 * @param {string} path - 请求路径
 * @param {Object} body - 请求体对象
 * @returns {Promise<any>}
 */
export const apiPost = (path, body, isBlob = false) =>
  apiRequest(
    path,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    },
    isBlob
  );

/**
 * 获取所有文章
 * @returns {Promise<Array>}
 */
export async function getAllArticles() {
  return apiGet("/api/v1/website/article/all/article");
}

/**
 * 获取全部的分类信息
 * @returns {Promise<Array>}
 */
export async function getAllCategories() {
  return apiGet("/api/v1/website/article/all/category");
}

/**
 * 获取全部的tag的统计数据
 * @returns {Promise<Array>}
 */
export async function getTagCounts() {
  return apiGet("/api/v1/website/article/all/tag");
}

/**
 * 根据分类 ID 获取文章列表
 * @param {string|number} categoryId - 分类 ID
 * @returns {Promise<Array>}
 */
export async function getArticlesByCategory(categoryId) {
  return apiGet(`/api/v1/website/article/category/${categoryId}`);
}

/**
 * 根据 ID 获取单篇文章
 * @param {string|number} articleId - 文章 ID
 * @returns {Promise<Object>}
 */
export async function getArticle(articleId) {
  return apiGet(`/api/v1/website/article/id/${articleId}`);
}

/**
 * 根据标签获取相关文章
 * @param {string} tag - 标签名称
 * @returns {Promise<Array>} - 相关文章列表
 */
export async function getArticlesByTag(tag) {
  return apiGet(`/api/v1/website/article/tag/${tag}`);
}

/**
 * 编辑文章内容
 * @param {string|number} articleId - 文章 ID
 * @param {Object} articleData - 文章内容数据
 * @returns {Promise<Object>}
 */
export async function editArticle(articleId, articleData) {
  return apiPost("/api/v1/website/article/edit/content", { article_id: articleId, content: articleData });
}

/**
 * 编辑文章元数据
 * @param {string|number} articleId - 文章 ID
 * @param {Object} metaData - 元数据对象
 * @returns {Promise<Object>}
 */
export async function editMeta(articleId, metaData) {
  return apiPost("/api/v1/website/article/edit/meta", { article_id: articleId, ...metaData });
}

/**
 * 更新文章的序号
 * @param {*} id
 * @param {*} serialNo
 * @returns
 */
export async function editSerialNo(id, serialNo) {
  return apiPost("/api/v1/website/article/edit/serialNo", { id, serialNo });
}

/**
 * 检查文章是否存在
 * @param {*} category
 * @param {*} title
 * @returns
 */
export async function editIsExist(category, title) {
  return apiPost("/api/v1/website/article/edit/exist", { category, title });
}

/** * 删除文章
 * @param {string|number} id - 文章 ID
 * @returns {Promise<Object>} - 返回删除结果
 */
export async function deleteArticle(id) {
  return apiPost("/api/v1/website/article/file/delete", { id });
}

/**
 * 将文章保存到缓存
 * @param {*} id
 * @returns
 */
export async function syncArticleToFile(id) {
  return apiPost("/api/v1/website/article/file/sync", { id });
}

/**
 * 添加新文章
 * @param {string} category - 文章分类
 * @param {string} title - 文章标题
 * @returns {Promise<Object>} - 返回新创建的文章信息
 */
export async function addArticle(category, title) {
  return apiPost("/api/v1/website/article/file/new", { category, title });
}

/**
 * 获取文章文件内容
 * @param {*} id - 文章 ID
 * @returns {Promise<Object>}
 */
export async function getArticleText(id) {
  return apiPost("/api/v1/website/article/file/text", { id });
}

/**
 * 获取隐私政策
 * @returns {Promise<Object>} - 返回用户信息
 */
export async function getPrivacyPolicy() {
  return apiGet("/api/v1/authorization/privacy");
}

/***
 * 用户登录
 */
export async function login(username, password) {
  return apiPost("/api/v1/authorization/login", { username, password });
}

/**
 * 用户注册
 */
export async function register(username, password, nickname) {
  return apiPost("/api/v1/authorization/register", { username, password, nickname });
}

/**
 * 刷新用户令牌
 * @returns {Promise<Object>} - 返回新的用户信息
 */
export async function refresh() {
  return apiPost("/api/v1/authorization/refresh");
}

/**
 * 用户登出
 * @returns {Promise<Object>} - 返回用户信息
 */
export async function logout() {
  return apiGet("/api/v1/authorization/logout");
}

/**
 * 更新用户头像
 * @param {string} avatar - 头像的 Base64 编码字符串
 */
export async function updateAvatar(avatar) {
  return apiPost("/api/v1/authorization/update/avatar", { avatar });
}

/**
 * 判断图像是不是存在
 */
export async function checkImageExit(category, name) {
  return apiPost("/api/v1/website/image/upload/check", { category, name });
}

/**
 *  获取全部的代码空间项目
 * @returns {Promise<Array>} - 返回代码空间项目列表
 */
export async function getAllAdBannerItem() {
  return apiGet("/api/v1/website/adbanner/all");
}

/**
 * 设置广告位
 * @param {*} ads - 广告位数组
 * @returns {Promise<Object>} - 返回设置结果
 */
export async function setAllAdBannerItems(ads) {
  return apiPost("/api/v1/website/adbanner/set", { ads });
}

/**
 * 获取导航信息
 * @returns {Promise<Array>} - 返回导航信息列表
 */
export async function getNavigation() {
  return apiGet("/api/v1/website/navs/all");
}

/**
 * 设置导航信息
 * @param {Array} navs - 导航信息数组，每个元素包含 { name, url, new }
 */
export async function setNavigation(navs) {
  return apiPost("/api/v1/website/navs/set", { navs });
}

/**
 * 获取指定分类下的所有图片
 * @param {*} category
 * @returns
 */
export async function allImageInCategory(category) {
  return apiPost(`/api/v1/website/image/category/all`, { category });
}

/**
 * 重命名图片
 * @param {*} category
 * @param {*} oldName
 * @param {*} newName
 * @returns {Promise<Object>} - 返回重命名结果
 */
export async function renameImage(category, oldName, newName) {
  return apiPost(`/api/v1/website/image/rename`, { category, oldName, newName });
}

/**
 * 删除图片
 * @param {*} category
 * @param {*} name
 * @returns {Promise<Object>} - 返回删除结果
 */
export async function deleteImage(category, name) {
  return apiPost(`/api/v1/website/image/delete`, { category, name });
}

/**
 * 获取所有缓存数据
 * @returns {Promise<Array>} - 返回所有缓存数据
 */
export async function getAllCache() {
  return apiGet(`/api/v1/resource/cache/all`);
}

/**
 * 下载缓存文件
 * @param {*} filename
 * @returns
 */
export async function downloadCacheFile(filename) {
  return apiPost(`/api/v1/resource/cache/download`, { filename }, true);
}

/**
 * 删除缓存文件
 * @param {*} filename
 * @returns
 */
export async function deleteCacheFile(filename) {
  return apiPost(`/api/v1/resource/cache/delete`, { filename });
}

/**
 * 获取所有评论
 * @param {string} article_id
 * @returns
 */
export async function getAllComments(article_id) {
  return apiPost(`/api/v1/website/comment/all`, { article_id });
}

/**
 * 添加评论
 * @param {string} article_id
 * @param {object} content
 * @param {string} parent_id
 * @returns
 */
export async function addComment(article_id, content, parent_id = "") {
  return apiPost(`/api/v1/website/comment/add`, { article_id, content, parent_id });
}

/**
 * 删除评论
 * @param {string} article_id
 * @param {string} comment_id
 * @returns
 */
export async function deleteComment(article_id, comment_id) {
  return apiPost(`/api/v1/website/comment/delete`, { article_id, comment_id });
}
