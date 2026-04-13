import js from '@eslint/js'
import pluginVue from 'eslint-plugin-vue'
import * as parserVue from 'vue-eslint-parser'
import configTypescript from '@typescript-eslint/eslint-plugin'
import parserTypescript from '@typescript-eslint/parser'
import pluginPrettier from 'eslint-plugin-prettier'
import configPrettier from 'eslint-config-prettier'

export default [
  {
    name: 'app/files-to-lint',
    files: ['**/*.{ts,mts,tsx,vue}'],
  },

  {
    name: 'app/files-to-ignore',
    ignores: [
      '**/dist/**',
      '**/dist-ssr/**',
      '**/coverage/**',
      '**/node_modules/**',
      '**/backend/**',
    ],
  },

  js.configs.recommended,

  ...pluginVue.configs['flat/recommended'],
  {
    name: 'app/vue-rules',
    files: ['**/*.vue'],
    languageOptions: {
      parser: parserVue,
      parserOptions: {
        parser: parserTypescript,
        extraFileExtensions: ['.vue'],
        sourceType: 'module',
      },
    },
    plugins: {
      '@typescript-eslint': configTypescript,
    },
    rules: {
      'vue/multi-word-component-names': 'off',
      'vue/no-v-html': 'off',
      'vue/attributes-order': 'off',
      'no-undef': 'off',
      'no-unused-vars': 'off',
      '@typescript-eslint/no-unused-vars': [
        'error',
        { argsIgnorePattern: '^_', varsIgnorePattern: '^_' },
      ],
    },
  },

  {
    name: 'app/typescript-rules',
    files: ['**/*.{ts,mts,tsx}'],
    languageOptions: {
      parser: parserTypescript,
      parserOptions: {
        sourceType: 'module',
      },
    },
    plugins: {
      '@typescript-eslint': configTypescript,
    },
    rules: {
      ...configTypescript.configs.recommended.rules,
      '@typescript-eslint/no-unused-vars': [
        'error',
        { argsIgnorePattern: '^_' },
      ],
      '@typescript-eslint/no-explicit-any': 'off',
      'no-undef': 'off',
    },
  },

  {
    name: 'app/prettier-rules',
    plugins: {
      prettier: pluginPrettier,
    },
    rules: {
      ...configPrettier.rules,
      'prettier/prettier': 'off',
    },
  },
]
