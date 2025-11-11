/**
 * 弹出文件选择对话框，返回选中的 Image 对象
 * @returns {Promise<File>}
 */
function selectImage() {
  const fileInput = document.getElementById("global-image-upload-input");
  return new Promise((resolve) => {
    // 清除上次的选择
    fileInput.value = "";
    fileInput.onchange = () => {
      resolve(fileInput.files[0] || null);
    };
    fileInput.click();
  });
}

/**
 * 选择文件
 * @returns {Promise<File>}
 */
function selectFile() {
  const fileInput = document.getElementById("global-file-upload-input");
  return new Promise((resolve) => {
    // 清除上次的选择
    fileInput.value = "";
    fileInput.onchange = () => {
      resolve(fileInput.files[0] || null);
    };
    fileInput.click();
  });
}

/**
 * 上传头像
 * @param {*} file
 * @param {*} fields
 * @returns {Promise<Response>}
 */
export async function uploadAvatar(name = "") {
  const uploadUrl = "/api/v1/website/image/upload/avatar";
  try {
    const file = await selectImage();
    if (!file) {
      console.warn("未选择文件");
      return null;
    }
    const formData = new FormData();
    formData.append("file", file);
    formData.append("name", name);
    const res = await fetch(uploadUrl, { method: "POST", body: formData });
    if (!res.ok) {
      console.error("上传头像失败:", res.statusText);
      return null;
    }
    return res.json();
  } catch (error) {
    console.error("上传头像失败:", error);
    return null;
  }
}

/**
 * 上传文章图像
 * @param {*} category
 * @param {*} name
 * @returns
 */
export async function uploadArticleImage(category, name) {
  const uploadUrl = "/api/v1/website/image/upload/article";
  try {
    const file = await selectImage();
    if (!file) {
      console.warn("未选择文件");
      return null;
    }
    const formData = new FormData();
    formData.append("file", file);
    formData.append("category", category);
    formData.append("name", name);
    const res = await fetch(uploadUrl, { method: "POST", body: formData });
    if (!res.ok) {
      console.error("上传文章图像失败:", res.statusText);
      return null;
    }
    return res.json();
  } catch (error) {
    console.error("上传文章图像失败:", error);
    return null;
  }
}

let copyImageFile = null;

/**
 * 设置剪贴板中的图像文件
 * @param {*} file
 */
export function setCopyImageFile(file) {
  copyImageFile = file;
}

/**
 * 从剪贴板上传图像
 * @param {*} category
 * @param {*} name
 * @returns
 */
export async function uploadArticleImageFromCopy(category, name) {
  const uploadUrl = "/api/v1/website/image/upload/article";
  try {
    const formData = new FormData();
    formData.append("file", copyImageFile);
    formData.append("category", category);
    formData.append("name", name);
    const res = await fetch(uploadUrl, { method: "POST", body: formData });
    if (!res.ok) {
      console.error("上传文章图像失败:", res.statusText);
      copyImageFile = null;
      return null;
    }
    return res.json();
  } catch (error) {
    console.error("上传文章图像失败:", error);
    copyImageFile = null;
    return null;
  }
}

/**
 * 上传文件
 * @param {string} type - 文件类型
 * @param {string} name - 文件名称
 * @returns {Promise<Response>}
 */
export async function uploadCacheFile(options = {}) {
  const { onSelected, onProgress, onError } = options;
  const uploadUrl = "/api/v1/resource/cache/upload";
  try {
    const file = await selectFile();
    if (!file) {
      console.warn("未选择文件");
      return null;
    }
    onSelected?.(file);
    const formData = new FormData();
    formData.append("file", file);
    const result = await new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest();
      xhr.open("POST", uploadUrl);

      xhr.upload.onprogress = (event) => {
        if (!onProgress) return;
        const detail = {
          loaded: event.loaded,
          total: event.lengthComputable ? event.total : file.size || 0,
        };
        onProgress(detail, file);
      };

      xhr.onload = () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          let data = null;
          if (xhr.responseText) {
            try {
              data = JSON.parse(xhr.responseText);
            } catch {
              data = xhr.responseText;
            }
          }
          resolve(data);
        } else {
          const error = new Error(`上传缓存文件失败: ${xhr.status} ${xhr.statusText}`);
          onError?.(error, file);
          reject(error);
        }
      };

      xhr.onerror = () => {
        const error = new Error("上传缓存文件失败");
        onError?.(error, file);
        reject(error);
      };

      xhr.send(formData);
    });
    return result;
  } catch (error) {
    console.error("上传缓存文件失败:", error);
    throw error;
  }
}
