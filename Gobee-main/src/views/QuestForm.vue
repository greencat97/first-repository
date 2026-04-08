<template>
  <div class="d-flex flex-column justify-content-center align-items-center px-4 min-vh-100">
    <div class="card gap-2">
    <div class="d-flex flex-column gap-3">
      <h1 class="display-1 fw-medium">Quest Map</h1>
      <img class="w-100 mb-3" style="max-width: 320px;" src="../assets/CityQuestHeroImage.png" alt="Quest Map" />
      <p class="text-center ">Get a fun out-door exercise challenge with your child today!</p>
    </div>
      <button class="btn btn-warning rounded-pill w-75 mb-3 fw-medium" @click="$router.push('/quest')">Start Quest</button>
    </div>
  </div>
</template>

<script>
</script>

<style scoped>
.card {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  max-width: 380px;
  border-radius: 24px;
  padding: 20px;
  justify-content: center;
  text-align: center;
}
</style>
