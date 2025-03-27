document.addEventListener('DOMContentLoaded', function () {
    const likeSections = document.querySelectorAll('.like-section');
  
    likeSections.forEach(section => {
      const button = section.querySelector('.like-btn');
      const likeCountSpan = section.querySelector('.like-count');
      const postId = section.getAttribute('data-post-id');
  
      button.addEventListener('click', function (e) {
        e.preventDefault();
  
        const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
  
        fetch("/ajax/like/", {
          method: 'POST',
          headers: {
            'X-CSRFToken': csrfToken,
            'Content-Type': 'application/x-www-form-urlencoded',
          },
          body: `post_id=${postId}`
        })
        .then(response => response.json())
        .then(data => {
          likeCountSpan.textContent = data.like_count;
          button.textContent = data.liked ? "❤️ Unlike" : "🤍 Like";
          button.setAttribute('data-liked', data.liked ? "true" : "false");
        });
      });
    });
  });