function openEditUserModal(id, name, username, role) {
    document.getElementById('edit_emp_id').value = id;
    document.getElementById('edit_first_name').value = name;
    document.getElementById('edit_username').value = username;
    const roleSelect = document.getElementById('edit_role');
    for(let i=0; i<roleSelect.options.length; i++) {
        if(roleSelect.options[i].value === role || roleSelect.options[i].text === role) {
            roleSelect.selectedIndex = i; break;
        }
    }
    document.getElementById('edit_password').value = ''; 
    new bootstrap.Modal(document.getElementById('editUserModal')).show();
}

function openEditRoleModal(id, roleName, currentPermissions) {
    document.getElementById('edit_role_id').value = id;
    document.getElementById('display_role_name').innerText = roleName;
    const checkboxes = document.querySelectorAll('#editRoleForm input[name="permissions"]');
    checkboxes.forEach(cb => cb.checked = false);
    if (currentPermissions) {
        const perms = currentPermissions.split(',');
        perms.forEach(p => {
            const cb = document.querySelector(`#editRoleForm input[value="${p.trim()}"]`);
            if (cb) cb.checked = true;
        });
    }
    new bootstrap.Modal(document.getElementById('editRoleModal')).show();
}

function viewPermissions(roleName, currentPermissions) {
    const perms = currentPermissions.split(',').map(p => p.trim());
    const menuItems = [
        { id: 'dashboard', name: 'แดชบอร์ด', icon: 'fa-gauge-high' },
        { id: 'add_order', name: 'รับออเดอร์ใหม่', icon: 'fa-plus-circle' },
        { id: 'manage_orders', name: 'มอบหมายงาน', icon: 'fa-list-check' },
        { id: 'laundry_queue', name: 'งานที่ต้องทำ', icon: 'fa-basket-shopping' },
        { id: 'completed_orders', name: 'ประวัติงานเสร็จสิ้น', icon: 'fa-clock-rotate-left' },
        { id: 'system_settings', name: 'ตั้งค่าราคาและระบบ', icon: 'fa-screwdriver-wrench' },
        { id: 'manage_users', name: 'ตั้งค่าผู้ใช้งาน', icon: 'fa-users-gear' }
    ];

    let html = '<div class="list-group rounded-3 overflow-hidden border shadow-sm">';
    menuItems.forEach(item => {
        const isChecked = perms.includes(item.id);
        html += `
            <div class="list-group-item d-flex align-items-center py-3 border-start-0 border-end-0">
                <div class="me-3">
                    ${isChecked 
                        ? '<i class="fa-solid fa-square-check text-primary fs-5"></i>' 
                        : '<i class="fa-solid fa-square-xmark text-danger fs-5" style="opacity: 0.5;"></i>'}
                </div>
                <div class="me-2 text-secondary" style="width: 25px; text-align: center;">
                    <i class="fa-solid ${item.icon}"></i>
                </div>
                <div class="${isChecked ? 'text-dark fw-bold' : 'text-muted'}">
                    ${item.name}
                </div>
            </div>`;
    });
    html += '</div>';

    Swal.fire({
        title: `<div class="mb-2" style="font-size: 0.9rem; color: #6c757d; font-weight: normal;">สิทธิ์การเข้าถึงเมนูของกลุ่ม</div><div class="text-primary">${roleName}</div>`,
        html: html,
        confirmButtonText: 'ปิดหน้าต่าง',
        confirmButtonColor: '#6c757d',
        customClass: { popup: 'rounded-4', title: 'pb-0' },
        width: '450px'
    });
}

function confirmAddUser() {
    const form = document.getElementById('addUserForm');
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }
    form.submit();
}

function confirmEditUser() {
    const form = document.getElementById('editUserForm');
    if (!form.checkValidity()) { form.reportValidity(); return; }
    Swal.fire({
        title: 'ยืนยันการแก้ไขข้อมูล?', icon: 'question', showCancelButton: true,
        confirmButtonColor: '#ffc107', cancelButtonColor: '#6c757d',
        confirmButtonText: 'อัปเดต', cancelButtonText: 'ยกเลิก', reverseButtons: true
    }).then((result) => { if (result.isConfirmed) form.submit(); });
}

function confirmDeleteUser(id, name) {
    Swal.fire({
        title: 'ลบผู้ใช้งาน?', html: `ต้องการลบบัญชี <b class="text-danger">${name}</b> ใช่หรือไม่?`,
        icon: 'warning', showCancelButton: true, confirmButtonColor: '#dc3545',
        cancelButtonColor: '#6c757d', confirmButtonText: 'ลบ', cancelButtonText: 'ยกเลิก', reverseButtons: true
    }).then((result) => { if (result.isConfirmed) document.getElementById('deleteForm-' + id).submit(); });
}

function confirmEditRole() {
    const form = document.getElementById('editRoleForm');
    Swal.fire({
        title: 'บันทึกการตั้งค่าสิทธิ์?', text: "การเข้าถึงเมนูของพนักงานจะถูกอัปเดตทันที",
        icon: 'question', showCancelButton: true, confirmButtonColor: '#0d6efd',
        cancelButtonColor: '#6c757d', confirmButtonText: 'บันทึกสิทธิ์', cancelButtonText: 'ยกเลิก', reverseButtons: true
    }).then((result) => { if (result.isConfirmed) form.submit(); });
}