/**
 * 弹出文件选择对话框，返回选中的 File 对象
 * @returns {Promise<File>}
 */
function selectFile() {
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
 * 上传头像
 * @param {*} file
 * @param {*} fields
 * @returns {Promise<Response>}
 */
export async function uploadAvatar(name = "") {
  const uploadUrl = "/api/v1/website/image/upload/avatar";
  try {
    const file = await selectFile();
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
    const file = await selectFile();
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
