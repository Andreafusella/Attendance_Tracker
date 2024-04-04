/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: [
    "./templates/**/*.{html,js}",
    "./node_modules/tw-elements/dist/js/**/*.js",
    "./node_modules/flowbite/**/*.js",
    "./templates/.html", "./templates/script/.js"
  ],
  theme: {
    extend: {
      backgroundImage:{
        "sfondo1": "url('/templates/immage/sfondo.jpg')",
        "sfondo2": "url('/templates/immage/sfondo2.jpg')",
        "sfondo3": "url('/templates/immage/bgwhite.jpg')",
        "sfondologo": "url('/templates/immage/9391712.png')"
      },
      animation:{
        'animation': 'bounce 1.5s infinite;',
      },
    },
  },
  plugins: [
    require("tailwindcss-animation-delay"),
    require("tw-elements/dist/plugin.cjs"),
    require("tailwindcss-animate"),
    require("daisyui"),
    require('flowbite/plugin'),
  ],
}

