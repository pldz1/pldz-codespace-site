/**
 * 通用 API 请求函数，自动处理请求、响应与错误
 * @param {string} path - 请求路径，例如 '/api/v1/articles/all'
 * @param {Object} [options] - Fetch 配置项
 * @returns {Promise<any>} - 返回后端返回的数据部分
 * @throws {Error} - 网络错误或 JSON 解析错误
 */
async function apiRequest(path, options = {}) {
  const response = await fetch(path, options);
  if (!response.ok) {
    console.error(`网络响应失败 (${response.status} ${response.statusText})`);
    return null;
  }

  let payload;
  try {
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
export const apiPost = (path, body) =>
  apiRequest(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

/**
 * 获取所有文章
 * @returns {Promise<Array>}
 */
export async function getAllArticles() {
  return apiGet("/api/v1/articles/all");
}

/**
 * 获取全部的分类信息
 * @returns {Promise<Array>}
 */
export async function getAllCategories() {
  return apiGet("/api/v1/categories");
}

/**
 * 根据分类 ID 获取文章列表
 * @param {string|number} categoryId - 分类 ID
 * @returns {Promise<Array>}
 */
export async function getArticlesByCategory(categoryId) {
  return apiGet(`/api/v1/articles/category/${categoryId}`);
}

/**
 * 根据 ID 获取单篇文章
 * @param {string|number} articleId - 文章 ID
 * @returns {Promise<Object>}
 */
export async function getArticle(articleId) {
  return apiGet(`/api/v1/articles/id/${articleId}`);
}

/**
 * 获取全部的tag的统计数据
 * @returns {Promise<Array>}
 */
export async function getTagCounts() {
  return apiGet("/api/v1/tag/counts");
}

/**
 * 根据标签获取相关文章
 * @param {string} tag - 标签名称
 * @returns {Promise<Array>} - 相关文章列表
 */
export async function getArticlesByTag(tag) {
  return apiGet(`/api/v1/articles/tag/${tag}`);
}

/**
 * 编辑文章内容
 * @param {string|number} articleId - 文章 ID
 * @param {Object} articleData - 文章内容数据
 * @returns {Promise<Object>}
 */
export async function editArticle(articleId, articleData) {
  return apiPost("/api/v1/articles/edit", { article_id: articleId, content: articleData });
}

/**
 * 编辑文章元数据
 * @param {string|number} articleId - 文章 ID
 * @param {Object} metaData - 元数据对象
 * @returns {Promise<Object>}
 */
export async function editMeta(articleId, metaData) {
  return apiPost("/api/v1/articles/metaedit", { article_id: articleId, ...metaData });
}

/**
 * 获取隐私政策
 * @returns {Promise<Object>} - 返回用户信息
 */
export async function getPrivacyPolicy() {
  return apiGet("/api/v1/auth/privacy");
}

/***
 * 用户登录
 */
export async function login(username, password) {
  return apiPost("/api/v1/auth/login", { username, password });
}

/**
 * 用户注册
 */
export async function register(username, password) {
  return apiPost("/api/v1/auth/register", { username, password });
}

/**
 * 刷新用户令牌
 * @returns {Promise<Object>} - 返回新的用户信息
 */
export async function refresh() {
  return apiPost("/api/v1/auth/refresh");
}

/**
 * 用户登出
 * @returns {Promise<Object>} - 返回用户信息
 */
export async function logout() {
  return apiGet("/api/v1/auth/logout");
}
