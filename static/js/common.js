// 通用JavaScript函数

// 显示加载提示
function showLoading(message) {
    // 可以在这里实现加载提示
    console.log('Loading: ' + message);
}

// 显示错误提示
function showError(message) {
    alert('错误: ' + message);
}

// 格式化数字
function formatNumber(num) {
    if (num >= 1000000000) {
        return (num / 1000000000).toFixed(2) + 'B';
    } else if (num >= 1000000) {
        return (num / 1000000).toFixed(2) + 'M';
    } else if (num >= 1000) {
        return (num / 1000).toFixed(2) + 'K';
    }
    return num.toString();
}

// 格式化日期
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('zh-CN');
}



