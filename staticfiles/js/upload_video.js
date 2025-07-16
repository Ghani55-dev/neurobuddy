document.addEventListener('DOMContentLoaded', function () {
  const form = document.getElementById('videoUploadForm');
  const videoInput = document.getElementById('video_file');
  const preview = document.getElementById('preview');
  const progress = document.getElementById('uploadProgress');
  const messageBox = document.getElementById('uploadMessage');

  // Show video preview
  videoInput.addEventListener('change', function () {
    const file = videoInput.files[0];
    if (file) {
      const url = URL.createObjectURL(file);
      preview.src = url;
      preview.style.display = 'block';
    }
  });

  // AJAX upload with progress
  form.addEventListener('submit', function (e) {
    e.preventDefault();

    const formData = new FormData(form);
    const xhr = new XMLHttpRequest();

    xhr.open('POST', '', true);

    xhr.upload.addEventListener('progress', function (e) {
      if (e.lengthComputable) {
        const percent = (e.loaded / e.total) * 100;
        progress.style.display = 'block';
        progress.value = percent;
      }
    });

    xhr.onload = function () {
      if (xhr.status === 200) {
        const response = JSON.parse(xhr.responseText);
        messageBox.innerHTML = `<p style="color:green;">${response.message}</p>`;
        form.reset();
        preview.style.display = 'none';
        progress.style.display = 'none';

        if (response.redirect_url) {
          setTimeout(() => window.location.href = response.redirect_url, 1500);
        }
      } else {
        messageBox.innerHTML = `<p style="color:red;">Upload failed. Try again.</p>`;
      }
    };

    xhr.send(formData);
  });
});
