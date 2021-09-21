// Product Review Save
// Credit: Code Artisan Lab - https://www.youtube.com/watch?v=7tyMyLCjKVg&list=PLgnySyq8qZmrxJvJbZC1eb7PD4bu0a-sB&index=31
$("#addForm").submit(function (e) {
	$.ajax({
		data: $(this).serialize(),
		method: $(this).attr('method'),
		url: $(this).attr('action'),
		dataType: 'json',
		success: function (res) {
			if (res.bool == true) {
				// $(".ajaxRes").html('Review has been added.');
				// Reset form button
				$("#reset").trigger('click');
				// Hide Add Review button
				$("#btn-review").hide();
				// Create data for rating
				var _html = '<span class="avg-stars">';
				for (var i = 1; i <= res.avg_reviews.avg_rating.toFixed(1); i++) {
					_html += '<i class="bi bi-star-fill text-warning"></i>';
				}
				_html += '</span>' 
				_html += '<span class="text-muted small avg-rating ms-2">' + res.avg_reviews.avg_rating.toFixed(1)
				_html += '</span>'
				// Prepend Data and remove previous element
				// Credit: https://stackoverflow.com/questions/24429015/jquery-append-text-only-once
				$(".rating-title").empty().prepend(_html);
				// create data for review
				var _html = '<blockquote class="blockquote text-right">';
				_html += '<cite title="Source Title">';
				for (var i = 1; i <= res.data.review_rating; i++) {
					_html += '<i class="bi bi-star-fill text-warning"></i>';
				}
				//Delete button & URL
				//Credit for url: https://stackoverflow.com/questions/68721529/update-existing-post-called-using-dictionary-using-ajax-django
				var url = "https://8000-aquamarine-panther-o9jbnzm2.ws-eu15.gitpod.io/products/delete-review/" +res.data.review_id; 
				_html += '<a href='+ url +' type="button" class="btn btn-danger btn-sm mb-2 ms-2 float-end">Delete</a>';
				_html += '</cite>';
				_html += '<p>' + res.data.review_text + '</p>';
				// Credit for first letter capitalize below: https://stackoverflow.com/questions/1026069/how-do-i-make-the-first-letter-of-a-string-uppercase-in-javascript
				_html += '<footer class="blockquote-footer">'+ res.data.user.charAt(0).toUpperCase()+res.data.user.slice(1) 
				_html += ', ';
				_html += '<span>' + res.data.created_on;
				_html += '</span>'
				_html += '</footer>';
				_html += '</blockquote>';
				_html += '<hr />';
				// Hide Add First Review text
				$(".no-data").hide();
				// Prepend Data
				$(".review-list").prepend(_html);
				// Hide Modal
				$("#productReview").modal('hide');
				// Add Avg Rating if no previous rating
				$(".avg-rating").text(res.avg_reviews.avg_rating.toFixed(1)).after("<span class='text-muted small'>/5</span>");
				// Remove No Rating text
				$(".no-rating").remove();
			}
		}
	});
	e.preventDefault();
});

// Edit Product Review 
$("#editForm").submit(function (e) {
	$.ajax({
		data: $(this).serialize(),
		method: $(this).attr('method'),
		url: $(this).attr('action'),
		dataType: 'json',
		success: function (res) {
			if (res.bool == true) {
				// $(".ajaxRes").html('Review has been added.');
				// Reset form button
				$("#reset").trigger('click');
				// Hide Add Review button
				// $("#btn-review").hide();
				// Create rating
				var _html = '<span class="avg-stars">';
				for (var i = 1; i <= res.avg_reviews.avg_rating.toFixed(1); i++) {
					_html += '<i class="bi bi-star-fill text-warning"></i>';
				}
				_html += '</span>' 
				_html += '<span class="text-muted small avg-rating ms-2">' + res.avg_reviews.avg_rating.toFixed(1)
				_html += '</span>'
				// Prepend Data and remove previous element
				// Credit: https://stackoverflow.com/questions/24429015/jquery-append-text-only-once
				$(".rating-title").empty().prepend(_html);
				// Create review
				var _html = '<blockquote class="blockquote text-right">';
				_html += '<cite title="Source Title">';
				for (var i = 1; i <= res.data.review_rating; i++) {
					_html += '<i class="bi bi-star-fill text-warning"></i>';
				}
				//Delete button & URL
				//Credit for url: https://stackoverflow.com/questions/68721529/update-existing-post-called-using-dictionary-using-ajax-django
				var url = "https://8000-aquamarine-panther-o9jbnzm2.ws-eu15.gitpod.io/products/delete-review/" +res.data.review_id; 
				_html += '<a href='+ url +' type="button" class="btn btn-danger btn-sm mb-2 ms-2 float-end">Delete</a>';
				_html += '</cite>';
				_html += '<p>' + res.data.review_text + '</p>';
				// Credit for first letter capitalize below: https://stackoverflow.com/questions/1026069/how-do-i-make-the-first-letter-of-a-string-uppercase-in-javascript
				_html += '<footer class="blockquote-footer">'+ res.data.user.charAt(0).toUpperCase()+res.data.user.slice(1) 
				_html += ', ';
				_html += '<span>' + res.data.created_on;
				_html += '</span>'
				_html += '</footer>';
				_html += '</blockquote>';
				_html += '<hr />';
				// Hide Add First Review text
				$(".no-data").hide();
				// Prepend Data
				$(".review-list").prepend(_html);
				// Hide Modal
				$("#editReview").modal('hide');
				// Add Avg Rating if no previous rating
				$(".avg-rating").text(res.avg_reviews.avg_rating.toFixed(1)).after("<span class='text-muted small'>/5</span>");
				// Remove No Rating text
				$(".no-rating").remove();
			}
		}
	});
	e.preventDefault();
});