document.addEventListener("DOMContentLoaded", function() {
    const filterBill = document.getElementById('filterBill');
    const filterCustomer = document.getElementById('filterCustomer');
    const filterDate = document.getElementById('filterDate');
    const pageSizeSelect = document.getElementById('pageSize');
    const searchBtn = document.getElementById('searchBtn');
    
    const rows = Array.from(document.querySelectorAll('.order-row:not(.empty-row)'));
    const noMatchRow = document.getElementById('noMatchRow');
    const emptyStateRow = document.getElementById('emptyStateRow');
    
    let currentPage = 1;

    function renderTable() {
        if (rows.length === 0) {
            document.getElementById('pageInfo').textContent = `แสดง 0 ถึง 0 จากทั้งหมด 0 รายการ`;
            renderPagination(1); 
            return;
        }

        const billVal = filterBill.value.toLowerCase();
        const cusVal = filterCustomer.value.toLowerCase();
        const dateVal = filterDate.value;
        const pageSize = parseInt(pageSizeSelect.value);

        let filteredRows = rows.filter(row => {
            const billText = row.querySelector('.col-bill').textContent.toLowerCase();
            const cusText = row.querySelector('.col-cus').textContent.toLowerCase();
            const dateText = row.getAttribute('data-date'); 

            const matchBill = billText.includes(billVal);
            const matchCus = cusText.includes(cusVal);
            const matchDate = dateVal === "" || dateText === dateVal;

            return matchBill && matchCus && matchDate;
        });

        const totalRows = filteredRows.length;
        const totalPages = Math.ceil(totalRows / pageSize) || 1;
        if (currentPage > totalPages) currentPage = totalPages;

        const startIndex = (currentPage - 1) * pageSize;
        const endIndex = startIndex + pageSize;

        rows.forEach(row => row.style.display = 'none');

        filteredRows.slice(startIndex, endIndex).forEach(row => row.style.display = '');

        if (totalRows === 0 && !emptyStateRow) {
            noMatchRow.style.display = '';
        } else {
            noMatchRow.style.display = 'none';
        }

        const endDisplay = Math.min(endIndex, totalRows);
        const startDisplay = totalRows > 0 ? startIndex + 1 : 0;
        document.getElementById('pageInfo').textContent = `แสดง ${startDisplay} ถึง ${endDisplay} จากทั้งหมด ${totalRows} รายการ`;

        renderPagination(totalPages);
    }

    function renderPagination(totalPages) {
        const paginationControls = document.getElementById('paginationControls');
        paginationControls.innerHTML = '';

        const createBtn = (label, target, active = false, disabled = false) => {
            const li = document.createElement('li');
            li.className = `page-item ${active ? 'active' : ''} ${disabled ? 'disabled' : ''}`;
            const a = document.createElement('a');
            a.className = 'page-link shadow-none';
            a.href = 'javascript:void(0);';
            a.textContent = label;
            
            if (!disabled) {
                a.addEventListener('click', () => {
                    currentPage = target;
                    renderTable();
                    window.scrollTo({ top: 0, behavior: 'smooth' }); 
                });
            }
            li.appendChild(a);
            return li;
        };

        paginationControls.appendChild(createBtn('ก่อนหน้า', currentPage - 1, false, currentPage === 1));

        for (let i = 1; i <= totalPages; i++) {
            paginationControls.appendChild(createBtn(i, i, currentPage === i));
        }

        paginationControls.appendChild(createBtn('ถัดไป', currentPage + 1, false, currentPage === totalPages || totalPages === 0));
    }

    searchBtn.addEventListener('click', () => { 
        currentPage = 1; 
        renderTable(); 
    });
    
    pageSizeSelect.addEventListener('change', () => { currentPage = 1; renderTable(); });

    // รันครั้งแรกเมื่อโหลดหน้า
    renderTable();
});