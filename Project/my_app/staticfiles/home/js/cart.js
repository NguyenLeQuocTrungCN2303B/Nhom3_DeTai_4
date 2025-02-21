var updateBtns = document.getElementsByClassName('update-cart');
for (i = 0; i < updateBtns.length; i++) {
    updateBtns[i].addEventListener('click', function () {
        var productId = this.dataset.product;
        var action = this.dataset.action;
        console.log('productId:', productId, 'Action:', action);

        // Kiểm tra người dùng đã đăng nhập chưa
        console.log('USER:', user);
        if (user === 'AnonymousUser') {
            Swal.fire({
                icon: "error",
                text: "Bạn chưa đăng nhập!",
                footer: '<a href="#">Đi tới trang đăng nhập?</a>',
            });
        } else {
            updateUserOrder(productId, action); // Gọi hàm xử lý giỏ hàng
        }
    });
}

// Hàm cập nhật giỏ hàng
function updateUserOrder(productId, action) {
    console.log('User is authenticated, sending data...');

    var url = '/update_item/'; // Địa chỉ API xử lý

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken, // CSRF token
        },
        body: JSON.stringify({ 'productId': productId, 'action': action }),
    })
    .then(response => response.json())
    .then(data => {
        console.log('data:', data);
        
        // Hiển thị thông báo thành công
        showAlert(function () {
            setTimeout(reloadPage, 10000); // Reload sau 10 giây
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
        title: "Đã cập nhật giỏ hàng",
        iconColor: "#696cff",
        showConfirmButton: false,
        timer: 1500, // Hiển thị alert trong 1.5 giây
    }).then(() => {
        location.reload(); // Reload ngay sau khi alert đóng
    });
}


// Hàm reload trang
function reloadPage() {
    location.reload(); // Reload trang hiện tại
}
