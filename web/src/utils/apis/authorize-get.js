import { apiGet, hostPrefix } from "./request.js";

/**
 * 获取隐私政策
 * @returns {Promise<Object>} - 返回用户信息
 */
export async function getPrivacyPolicy() {
  return apiGet(`${hostPrefix}/authorization/privacy`);
}

/**
 * 获得全部的用户信息
 * @returns {Promise<Object>} - 返回所有用户信息
 */
export async function getAllUsers() {
  return apiGet(`${hostPrefix}/authorization/usermanagement/all`);
}
