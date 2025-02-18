var updateBtns = document.getElementsByClassName('update-cart')
for(i=0;i<updateBtns.length;i++){
    updateBtns[i].addEventListener('click', function(){
        var productId = this.dataset.product
        var action = this.dataset.action
        updateUserOrder(productId, action)
    })
}

function updateUserOrder(productId, action) {
    console.log('User is authenticated, sending data...');

    var url = '/update_item/';

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({ 'productId': productId, 'action': action })
    })
    .then(response => response.json())
    .then(data => {
        console.log('data:', data);

        // Gọi hàm showAlert và truyền callback reloadPage
        showAlert(function() {
            setTimeout(reloadPage, 10000); // Chờ 2 giây trước khi reload
        });
    })
    .catch(error => {
        console.error('Lỗi khi cập nhật giỏ hàng:', error);
        Swal.fire({
            icon: "error",
            title: "Lỗi!",
            text: "Không thể thêm vào giỏ hàng, vui lòng thử lại.",
            confirmButtonColor: "#d33"
        });
    });
}

// Hàm hiển thị alert và gọi callback sau khi alert đóng
function showAlert(callback) {
    Swal.fire({
        icon: "success",
        title: "Đã thêm vào giỏ hàng",
        iconColor: "#696cff",
        showConfirmButton: false,
        timer: 1500
    }).then(() => {
        if (callback) callback(); // Gọi callback sau khi alert đóng
    });
}

// Hàm reload trang
function reloadPage() {
    location.reload();
}


