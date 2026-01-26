import * as React from "react"
import { useFormContext } from "react-hook-form"
import { cn } from "../../lib/utils"
import { Label } from "./label"

const Form = ({ children, ...props }) => {
  return <form {...props}>{children}</form>
}

const FormField = ({ name, render }) => {
  const methods = useFormContext()
  return render({
    field: {
      value: methods.watch(name),
      onChange: (value) => methods.setValue(name, value),
      onBlur: () => methods.trigger(name),
    },
    fieldState: methods.formState.errors[name] ? { error: methods.formState.errors[name] } : {},
  })
}

const FormItem = React.forwardRef(({ className, ...props }, ref) => {
  return (
    <div ref={ref} className={cn("space-y-2", className)} {...props} />
  )
})
FormItem.displayName = "FormItem"

const FormLabel = React.forwardRef(({ className, ...props }, ref) => {
  return (
    <Label
      ref={ref}
      className={cn(className)}
      {...props}
    />
  )
})
FormLabel.displayName = "FormLabel"

const FormControl = React.forwardRef(({ ...props }, ref) => {
  return <div ref={ref} {...props} />
})
FormControl.displayName = "FormControl"

const FormDescription = React.forwardRef(({ className, ...props }, ref) => {
  return (
    <p
      ref={ref}
      className={cn("text-sm text-muted-foreground", className)}
      {...props}
    />
  )
})
FormDescription.displayName = "FormDescription"

const FormMessage = React.forwardRef(({ className, children, ...props }, ref) => {
  if (!children) return null
  return (
    <p
      ref={ref}
      className={cn("text-sm font-medium text-destructive", className)}
      {...props}
    >
      {children}
    </p>
  )
})
FormMessage.displayName = "FormMessage"

export {
  Form,
  FormField,
  FormItem,
  FormLabel,
  FormControl,
  FormDescription,
  FormMessage,
}
