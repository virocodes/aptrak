$(document).ready(function() {
    $('.status-dropdown').change(function() {
        let applicationId = $(this).data('id');
        let newStatus = $(this).val();
        $.ajax({
            url: '/update/' + applicationId,
            method: 'POST',
            data: {field: 'status', value: newStatus},
            success: function(response) {
                location.replace(location.href);
            },
            error: function(xhr, status, error) {
                alert('Failed to update: ' + xhr.responseText);
            }
        });
    });
});

function toggleForm() {
    var formContainer = document.getElementById('formContainer');
    var toggleButton = document.querySelector('.toggle-button');
    if (formContainer.style.display === 'none' || formContainer.style.display === '') {
      formContainer.style.display = 'block';
      toggleButton.style.backgroundColor = '#0056b3';
    } else {
      formContainer.style.display = 'none';
      toggleButton.style.backgroundColor = '#007BFF';
    }
}

function toggleForm2() {
    var formContainer = document.getElementById('formContainer2');
    var toggleButton = document.querySelector('.toggle-button2');
    if (formContainer.style.display === 'none' || formContainer.style.display === '') {
      formContainer.style.display = 'block';
      toggleButton.style.backgroundColor = '#0056b3';
    } else {
      formContainer.style.display = 'none';
      toggleButton.style.backgroundColor = '#007BFF';
    }
}


function editField(field) {
    document.getElementById(field).classList.add('hidden');
    document.getElementById('edit-' + field).classList.add('hidden');
    document.getElementById(field + '-input').classList.remove('hidden');
    document.getElementById('save-' + field).classList.remove('hidden');

    textareas = document.querySelectorAll('textarea');
    textareas.forEach((area) => {
        area.style.height = 'auto';
        area.style.height = (area.scrollHeight) + 'px';
    })
}

// Function to handle saving a field
function saveField(field, applicationId) {
    let newValue = document.getElementById(field + '-input').value;
    $.ajax({
        url: '/update/' + applicationId,
        method: 'POST',
        data: { field: field, value: newValue },
        success: function(response) {
            document.getElementById(field).textContent = newValue;
            document.getElementById(field).classList.remove('hidden');
            document.getElementById('edit-' + field).remove('hidden');
            document.getElementById(field + '-input').classList.add('hidden');
            document.getElementById('save-' + field).classList.add('hidden');
            location.replace(location.href); // Reload the page
        },
        error: function(xhr, status, error) {
            alert('Failed to update: ' + xhr.responseText);
        }
    });
}

$('textarea').on('input', function () {
    this.style.height = 'auto';

    this.style.height = 
        (this.scrollHeight) + 'px';
});

// document.onload = () => {
//     textareas = document.getElementsByName();
//     textareas.forEach((area) => {
//         area.style.height = 'auto';

//         area.style.height = (this.scrollHeight) + 'px';
//     })
// }
