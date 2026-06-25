const STORAGE_KEY_PREFIX = 'streaming-site-rating';
const STAR_COUNT = 5;

const buildRatingText = (rating, total) => {
  return rating
    ? `You rated ${rating} out of ${total} stars ⭐`
    : `Tap a star to rate this stream.`;
};

const saveRating = (groupId, rating) => {
  localStorage.setItem(`${STORAGE_KEY_PREFIX}:${groupId}`, String(rating));
};

const loadRating = (groupId) => {
  const stored = localStorage.getItem(`${STORAGE_KEY_PREFIX}:${groupId}`);
  const value = Number(stored);
  return Number.isInteger(value) && value > 0 ? value : 0;
};

const updateStars = (stars, rating) => {
  stars.forEach((star, index) => {
    const isActive = index < rating;
    star.classList.toggle('active', isActive);
    star.classList.toggle('hover', false);
    star.setAttribute('aria-checked', String(isActive));
  });
};

const highlightStars = (stars, rating) => {
  stars.forEach((star, index) => {
    star.classList.toggle('hover', index < rating);
  });
};

const initStarGroups = () => {
  const starGroups = document.querySelectorAll('.stars');
  if (!starGroups.length) return;

  starGroups.forEach((group, groupIndex) => {
    const stars = Array.from(group.querySelectorAll('span'));
    const result = group.parentElement?.querySelector('.result');
    const groupId = group.dataset.ratingId || `default-${groupIndex}`;
    let currentRating = loadRating(groupId);

    group.setAttribute('role', 'radiogroup');
    group.setAttribute('aria-label', 'Star rating');

    updateStars(stars, currentRating);
    if (result) result.textContent = buildRatingText(currentRating, stars.length || STAR_COUNT);

    const setRating = (rating) => {
      currentRating = rating;
      updateStars(stars, rating);
      if (result) result.textContent = buildRatingText(rating, stars.length || STAR_COUNT);
      saveRating(groupId, rating);
    };

    stars.forEach((star, index) => {
      const ratingValue = index + 1;
      star.setAttribute('role', 'radio');
      star.setAttribute('tabindex', '0');
      star.setAttribute('aria-label', `${ratingValue} out of ${stars.length} stars`);
      star.setAttribute('aria-checked', 'false');

      const activate = () => setRating(ratingValue);

      star.addEventListener('click', activate);

      star.addEventListener('keydown', (event) => {
        if (event.key === 'Enter' || event.key === ' ') {
          event.preventDefault();
          activate();
        }
      });

      star.addEventListener('mouseover', () => highlightStars(stars, ratingValue));
      star.addEventListener('focus', () => highlightStars(stars, ratingValue));
      star.addEventListener('mouseleave', () => updateStars(stars, currentRating));
      star.addEventListener('blur', () => updateStars(stars, currentRating));
    });
  });
};

document.addEventListener('DOMContentLoaded', initStarGroups);
