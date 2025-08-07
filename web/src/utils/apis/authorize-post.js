import { apiPost, hostPrefix } from "./request.js";

/***
 * 用户登录
 */
export async function login(username, password) {
  return apiPost(`${hostPrefix}/authorization/login`, { username, password });
}

/**
 * 用户注册
 */
export async function register(username, password, nickname) {
  return apiPost(`${hostPrefix}/authorization/register`, { username, password, nickname });
}

/**
 * 刷新用户令牌
 * @returns {Promise<Object>} - 返回新的用户信息
 */
export async function refresh() {
  return apiPost(`${hostPrefix}/authorization/refresh`);
}

/**
 * 用户登出
 * @returns {Promise<Object>} - 返回用户信息
 */
export async function logout() {
  return apiGet(`${hostPrefix}/authorization/logout`);
}

/**
 * 更新用户头像
 * @param {string} avatar - 头像的 Base64 编码字符串
 */
export async function updateAvatar(avatar) {
  return apiPost(`${hostPrefix}/authorization/update/avatar`, { avatar });
}

/**
 * 删除用户
 * @param {string} username - 被删除的用户名
 * @returns {Promise<Object>} - 返回删除结果
 */
export async function deleteUserByUsername(username) {
  return apiPost(`${hostPrefix}/authorization/usermanagement/delete`, { username });
}
