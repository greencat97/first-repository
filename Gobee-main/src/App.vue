<template>
  <div id="app">
    <router-view />

    <nav class="bottom-nav">
      <router-link to="/" class="nav-item">
        <img src="@/assets/Home.svg" />
        <span>Home</span>
      </router-link>

      <router-link to="/quest" class="nav-item">
        <img src="@/assets/QuestMap.svg" />
        <span>City Quest</span>
      </router-link>

      <router-link to="/chef" class="nav-item">
        <img src="@/assets/ChefCam.svg" />
        <span>Chef Cam</span>
      </router-link>

      <router-link to="/account" class="nav-item">
        <img src="@/assets/Account.svg" />
        <span>Account</span>
      </router-link>
    </nav>
  </div>
</template>

<style>
html, body {
  margin: 0;
  padding: 0;
  height: 100%;
}

#app {
  position: relative;
  min-height: 100vh;
  width: 100vw;
}

#app::before {
  content: "";
  position: fixed;  
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;

  background-image: url('./assets/CityQuestPage.png');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;

  z-index: -1;  
}

.bottom-nav {
  position: fixed;
  bottom: 0;
  width: 100%;
  height: 70px;

  display: flex;
  justify-content: space-around;
  align-items: center;

  background: white;
  border-top: 1px solid #ddd;
}

.nav-item {
  display: flex;
  flex-direction: column;  
  align-items: center;
  justify-content: center;

  text-decoration: none;
  color: #666;
  font-size: 12px;
}

/* icon */
.nav-item img {
  width: 24px;
  height: 24px;
  margin-bottom: 4px;
}

.nav-item.router-link-active {
  color: #ff8c42; 
  filter: brightness(0) saturate(100%) invert(57%) sepia(93%) saturate(500%) hue-rotate(330deg);
  transform: scale(1.05);
}
</style>