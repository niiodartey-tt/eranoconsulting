import { useForm, UseFormProps } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import DOMPurify from 'isomorphic-dompurify';

// Input sanitization
export const sanitizeInput = (value: any): any => {
  if (typeof value === 'string') {
    return DOMPurify.sanitize(value, {
      ALLOWED_TAGS: [],
      ALLOWED_ATTR: [],
    });
  }
  
  if (typeof value === 'object' && value !== null) {
    const sanitized: any = {};
    for (const key in value) {
      if (value.hasOwnProperty(key)) {
        sanitized[key] = sanitizeInput(value[key]);
      }
    }
    return sanitized;
  }
  
  return value;
};

// Secure form hook
export function useSecureForm<TSchema extends z.ZodType<any, any>>(
  schema: TSchema,
  options?: UseFormProps<z.infer<TSchema>>
) {
  const form = useForm<z.infer<TSchema>>({
    ...options,
    resolver: zodResolver(schema),
  });
  
  const originalHandleSubmit = form.handleSubmit;
  
  // Override handleSubmit to sanitize inputs
  form.handleSubmit = (onValid, onInvalid) => {
    return originalHandleSubmit(
      (data) => {
        const sanitizedData = sanitizeInput(data);
        return onValid(sanitizedData);
      },
      onInvalid
    );
  };
  
  return form;
}

// Common validation schemas
export const authSchemas = {
  login: z.object({
    email: z
      .string()
      .email('Invalid email address')
      .max(255, 'Email too long')
      .transform((val) => val.toLowerCase()),
    password: z
      .string()
      .min(8, 'Password must be at least 8 characters')
      .max(128, 'Password too long'),
  }),
  
  register: z.object({
    email: z
      .string()
      .email('Invalid email address')
      .max(255, 'Email too long')
      .transform((val) => val.toLowerCase()),
    password: z
      .string()
      .min(8, 'Password must be at least 8 characters')
      .max(128, 'Password too long')
      .regex(
        /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]/,
        'Password must contain uppercase, lowercase, number, and special character'
      ),
    confirmPassword: z.string(),
    fullName: z
      .string()
      .min(2, 'Name too short')
      .max(255, 'Name too long')
      .optional(),
  }).refine((data) => data.password === data.confirmPassword, {
    message: "Passwords don't match",
    path: ['confirmPassword'],
  }),
};
