/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        '../templates/**/*.html',
        '../../templates/**/*.html',
        '../../**/templates/**/*.html',
    ],
    theme: {
        extend: {
            colors: {
                'bg': '#151c27',
                'bg-nav': '#111720',
                'accent': '#c8f535',
                'teal-from': '#b8ece6',
                'teal-to': '#5bc4be',
                'teal-icon': '#1a4a52',
                'text-main': '#e8f4f0',
                'text-muted': '#7ab5ae',
                'border-subtle': '#2a3f4a',
            },
            fontFamily: {
                'mono': ['"Roboto Mono"', 'monospace'],
                'heading': ['"Inter"', 'sans-serif'],
                'body': ['"Inter"', 'sans-serif'],
            }
        },
    },
    plugins: [
        require('@tailwindcss/forms'),
        require('@tailwindcss/typography'),
        require('@tailwindcss/aspect-ratio'),
    ],
}