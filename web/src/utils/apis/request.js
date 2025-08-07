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

export const hostPrefix = "/api/v1";
export const webSitePrefix = hostPrefix + "/website";
