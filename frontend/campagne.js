document.addEventListener("DOMContentLoaded", function () {
  const form = document.querySelector("form");

  form.addEventListener("submit", function (event) {
      event.preventDefault();

      const campagne = document.getElementById("campagne").value;
      const zone = document.getElementById("zone").value;
      const lieudit = document.getElementById("lieudit").value;
      const protection = document.getElementById("protection").value;
      const bateau = document.getElementById("bateau").value;
      const pilote = document.getElementById("pilote").value;
      const equipage = document.getElementById("equipage").value;
      const partaires = document.getElementById("partaires").value;

      if (!campagne || !zone || !lieudit || !protection || !bateau || !pilote || !equipage || !partaires) {
          alert("Vous devez remplir toutes les donnees.");
          return;
      }

      const formData = {
          campagne,
          zone,
          lieudit,
          protection,
          bateau,
          pilote,
          equipage,
          partaires
      };

      localStorage.setItem("campagneData", JSON.stringify(formData));
  });
});
