/**
 * 按照日期对文章进行排序
 * @param {*} articles
 * @returns
 */
export function sortByDate(articles) {
  return articles.sort((a, b) => new Date(b.date) - new Date(a.date));
}

/**
 * 按照浏览量对文章进行排序
 * @param {*} articles
 * @returns
 */
export function sortByViews(articles) {
  return articles.sort((a, b) => b.views - a.views);
}

/**
 * 按照序列号对文章进行排序
 * @param {*} articles
 * @returns
 */
export function sortBySerialNo(articles) {
  return articles.sort((a, b) => a.serialNo - b.serialNo);
}
