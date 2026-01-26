import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Input } from './ui/input';
import { Select } from './ui/select';
import {
  Form,
  FormField,
  FormItem,
  FormLabel,
  FormControl,
  FormMessage,
} from './ui/form';

// Relationship types (basati su backend/app/utils/constants.py)
const RELATIONSHIP_OPTIONS = [
  { value: 'madre', label: 'Madre' },
  { value: 'padre', label: 'Padre' },
  { value: 'genitore', label: 'Genitore' },
  { value: 'fratello', label: 'Fratello' },
  { value: 'sorella', label: 'Sorella' },
  { value: 'figlio', label: 'Figlio' },
  { value: 'figlia', label: 'Figlia' },
  { value: 'amico', label: 'Amico' },
  { value: 'coniuge', label: 'Coniuge' },
  { value: 'partner', label: 'Partner' },
  { value: 'assistente', label: 'Assistente' },
  { value: 'manager', label: 'Manager' },
  { value: 'altro', label: 'Altro' },
  { value: 'coinquilino', label: 'Coinquilino' },
  { value: 'medico', label: 'Medico' },
  { value: 'emergenza', label: 'Emergenza' },
  { value: 'membro della famiglia', label: 'Membro della Famiglia' },
  { value: 'docente', label: 'Docente' },
  { value: 'badante', label: 'Badante' },
  { value: 'tutore', label: 'Tutore' },
  { value: 'assistente sociale', label: 'Assistente Sociale' },
  { value: 'scuola', label: 'Scuola' },
  { value: 'centro diurno', label: 'Centro Diurno' },
];

// Schema di validazione Zod
const personSchema = z.object({
  name: z.string().min(2, 'Il nome deve essere di almeno 2 caratteri').max(50, 'Il nome non può superare i 50 caratteri'),
  surname: z.string().min(2, 'Il cognome deve essere di almeno 2 caratteri').max(50, 'Il cognome non può superare i 50 caratteri'),
  birthday: z.string().min(1, 'La data di nascita è obbligatoria').refine(
    (date) => {
      const dateObj = new Date(date);
      const today = new Date();
      return dateObj <= today && dateObj.getFullYear() >= 1900;
    },
    {
      message: 'La data di nascita deve essere nel passato e non prima del 1900',
    }
  ),
  relationship: z.string().min(1, 'La relazione è obbligatoria'),
});

const PersonForm = ({ onSubmit, defaultValues, isPatient = false }) => {
  const form = useForm({
    resolver: zodResolver(personSchema),
    defaultValues: defaultValues || {
      name: '',
      surname: '',
      birthday: '',
      relationship: 'altro',
    },
  });

  const handleSubmit = (data) => {
    onSubmit(data);
  };

  return (
    <Form onSubmit={form.handleSubmit(handleSubmit)}>
      <div className="space-y-4">
        <FormField
          name="name"
          render={({ field, fieldState }) => (
            <FormItem>
              <FormLabel>Nome *</FormLabel>
              <FormControl>
                <Input
                  placeholder="Inserisci il nome"
                  {...field}
                  className={fieldState.error ? 'border-destructive' : ''}
                />
              </FormControl>
              {fieldState.error && (
                <FormMessage>{fieldState.error.message}</FormMessage>
              )}
            </FormItem>
          )}
        />

        <FormField
          name="surname"
          render={({ field, fieldState }) => (
            <FormItem>
              <FormLabel>Cognome *</FormLabel>
              <FormControl>
                <Input
                  placeholder="Inserisci il cognome"
                  {...field}
                  className={fieldState.error ? 'border-destructive' : ''}
                />
              </FormControl>
              {fieldState.error && (
                <FormMessage>{fieldState.error.message}</FormMessage>
              )}
            </FormItem>
          )}
        />

        <FormField
          name="birthday"
          render={({ field, fieldState }) => (
            <FormItem>
              <FormLabel>Data di Nascita *</FormLabel>
              <FormControl>
                <Input
                  type="date"
                  max={new Date().toISOString().split('T')[0]}
                  {...field}
                  className={fieldState.error ? 'border-destructive' : ''}
                />
              </FormControl>
              {fieldState.error && (
                <FormMessage>{fieldState.error.message}</FormMessage>
              )}
            </FormItem>
          )}
        />

        <FormField
          name="relationship"
          render={({ field, fieldState }) => (
            <FormItem>
              <FormLabel>Relazione *</FormLabel>
              <FormControl>
                <Select
                  {...field}
                  className={fieldState.error ? 'border-destructive' : ''}
                  onChange={(e) => field.onChange(e.target.value)}
                >
                  {RELATIONSHIP_OPTIONS.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </Select>
              </FormControl>
              {fieldState.error && (
                <FormMessage>{fieldState.error.message}</FormMessage>
              )}
            </FormItem>
          )}
        />
      </div>
    </Form>
  );
};

export default PersonForm;
