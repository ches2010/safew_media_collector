// 通用工具函数
function formatDate(timestamp) {
    if (!timestamp) return '未知时间';
    const date = new Date(timestamp * 1000);
    return date.toLocaleString();
}

function formatDuration(seconds) {
    if (!seconds) return '0:00';
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
}

// 图片懒加载初始化
document.addEventListener('DOMContentLoaded', () => {
    // 可以在这里添加图片懒加载逻辑
});