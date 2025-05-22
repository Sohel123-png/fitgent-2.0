// FitGen App JavaScript

// Register Service Worker for PWA and notifications
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/static/service-worker.js')
      .then(registration => {
        console.log('ServiceWorker registration successful with scope: ', registration.scope);
        
        // Check for notification permission
        if ('Notification' in window) {
          if (Notification.permission === 'granted') {
            console.log('Notification permission already granted');
            subscribeUserToPush(registration);
          } else if (Notification.permission !== 'denied') {
            // We need to ask for permission
            document.getElementById('enableNotificationsBtn')?.addEventListener('click', () => {
              requestNotificationPermission(registration);
            });
          }
        }
      })
      .catch(error => {
        console.error('ServiceWorker registration failed: ', error);
      });
  });
}

// Request notification permission
async function requestNotificationPermission(registration) {
  try {
    const permission = await Notification.requestPermission();
    if (permission === 'granted') {
      console.log('Notification permission granted!');
      subscribeUserToPush(registration);
      
      // Show success message
      alert('Notifications enabled! You will now receive fitness alerts on your device.');
    } else {
      console.log('Notification permission denied');
    }
  } catch (error) {
    console.error('Error requesting notification permission:', error);
  }
}

// Subscribe user to push notifications
async function subscribeUserToPush(registration) {
  try {
    // This would normally communicate with your server to get the VAPID public key
    // For demo purposes, we're using a placeholder
    const publicKey = 'BEl62iUYgUivxIkv69yViEuiBIa-Ib9-SkvMeAtA3LFgDzkrxZJjSgSnfckjBJuBkr3qBUYIHBQFLXYp5Nksh8U';
    
    const subscription = await registration.pushManager.subscribe({
      userVisibleOnly: true,
      applicationServerKey: urlBase64ToUint8Array(publicKey)
    });
    
    console.log('User is subscribed:', subscription);
    
    // Send the subscription to your server
    await saveSubscription(subscription);
  } catch (error) {
    console.error('Failed to subscribe the user:', error);
  }
}

// Save subscription on server
async function saveSubscription(subscription) {
  const token = localStorage.getItem('token');
  if (!token) return;
  
  try {
    const response = await fetch('/api/notifications/subscribe', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(subscription)
    });
    
    if (response.ok) {
      console.log('Subscription saved on server');
    } else {
      console.error('Failed to save subscription on server');
    }
  } catch (error) {
    console.error('Error saving subscription:', error);
  }
}

// Helper function to convert base64 to Uint8Array
function urlBase64ToUint8Array(base64String) {
  const padding = '='.repeat((4 - base64String.length % 4) % 4);
  const base64 = (base64String + padding)
    .replace(/-/g, '+')
    .replace(/_/g, '/');

  const rawData = window.atob(base64);
  const outputArray = new Uint8Array(rawData.length);

  for (let i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i);
  }
  return outputArray;
}

// Sync with Google Fit
async function syncGoogleFit() {
  const syncButton = document.getElementById('syncGoogleFitBtn');
  if (!syncButton) return;
  
  try {
    // Show loading state
    syncButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Syncing...';
    syncButton.disabled = true;
    
    // Call the sync endpoint
    const response = await fetch('/sync-google-fit');
    const data = await response.json();
    
    if (data.success) {
      // Reload the page to show updated data
      window.location.reload();
    } else {
      alert('Error syncing with Google Fit: ' + (data.error || 'Unknown error'));
      
      // Reset button
      syncButton.innerHTML = '<i class="fas fa-sync-alt"></i> Sync Google Fit';
      syncButton.disabled = false;
    }
  } catch (error) {
    console.error('Error:', error);
    alert('An error occurred while syncing with Google Fit. Please try again.');
    
    // Reset button
    syncButton.innerHTML = '<i class="fas fa-sync-alt"></i> Sync Google Fit';
    syncButton.disabled = false;
  }
}

// Update notification settings
async function updateNotificationSettings() {
  const token = localStorage.getItem('token');
  if (!token) return;
  
  const settings = {
    step_goal: document.getElementById('stepGoalNotif')?.checked || false,
    workout_reminders: document.getElementById('workoutRemindersNotif')?.checked || false,
    water_reminders: document.getElementById('waterRemindersNotif')?.checked || false,
    sleep_reminders: document.getElementById('sleepRemindersNotif')?.checked || false
  };
  
  try {
    const response = await fetch('/api/fitness/notifications/settings', {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(settings)
    });
    
    if (response.ok) {
      alert('Notification settings updated successfully');
    } else {
      alert('Failed to update notification settings');
    }
  } catch (error) {
    console.error('Error updating notification settings:', error);
    alert('An error occurred while updating notification settings');
  }
}

// Initialize event listeners when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  // Sync Google Fit button
  const syncButton = document.getElementById('syncGoogleFitBtn');
  if (syncButton) {
    syncButton.addEventListener('click', syncGoogleFit);
  }
  
  // Notification settings form
  const notificationForm = document.getElementById('notificationSettingsForm');
  if (notificationForm) {
    notificationForm.addEventListener('submit', (e) => {
      e.preventDefault();
      updateNotificationSettings();
    });
  }
  
  // Logout button
  const logoutBtn = document.getElementById('logoutBtn');
  if (logoutBtn) {
    logoutBtn.addEventListener('click', () => {
      localStorage.removeItem('token');
      window.location.href = '/login';
    });
  }
  
  // Check if user is logged in
  const token = localStorage.getItem('token');
  if (!token && window.location.pathname !== '/login' && window.location.pathname !== '/signup') {
    window.location.href = '/login';
  }
});
