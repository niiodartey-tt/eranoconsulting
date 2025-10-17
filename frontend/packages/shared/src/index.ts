// Export all your shared utilities
export * from './lib/auth';
export * from './components/ui';
export * from './hooks';
export * from './utils';
export * from './types';
```

3. **Verify your directory structure has source files:**
```
frontend/packages/shared/
├── package.json
├── tsup.config.ts
├── tsconfig.json
└── src/
    ├── index.ts
    ├── lib/
    ├── components/
    ├── hooks/
    └── utils/
