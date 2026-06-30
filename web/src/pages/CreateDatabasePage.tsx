import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useForm, Controller } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { useMutation } from '@tanstack/react-query'
import Box from '@mui/material/Box'
import Paper from '@mui/material/Paper'
import Typography from '@mui/material/Typography'
import TextField from '@mui/material/TextField'
import MenuItem from '@mui/material/MenuItem'
import Button from '@mui/material/Button'
import Alert from '@mui/material/Alert'
import { createDatabaseSchema, type CreateDatabaseForm } from './createSchema'
import { createDatabase } from '../api/databases'
import { ENGINE_LIST, ENGINE_META } from '../config/engines'
import type { CreateDatabaseRequest, EngineType } from '../api/types'
import EngineIcon from '../components/EngineIcon'

export default function CreateDatabasePage() {
  const navigate = useNavigate()
  const [submitError, setSubmitError] = useState<string | null>(null)

  const {
    register,
    handleSubmit,
    watch,
    control,
    formState: { errors },
  } = useForm<CreateDatabaseForm>({
    resolver: zodResolver(createDatabaseSchema),
    defaultValues: {
      name: '',
      engine_type: 'clickhouse',
      cpu: '500m',
      memory: '1Gi',
      storage: '10Gi',
      replicas: 1,
      shards: 1,
    },
  })

  const engine = watch('engine_type') as EngineType
  const hasShards = ENGINE_META[engine]?.hasShards

  const mutation = useMutation({
    mutationFn: createDatabase,
    onSuccess: () => navigate('/databases'),
    onError: (e: Error) => setSubmitError(e.message),
  })

  const onSubmit = (form: CreateDatabaseForm) => {
    setSubmitError(null)
    const payload: CreateDatabaseRequest = {
      name: form.name,
      engine_type: form.engine_type,
      cpu: form.cpu,
      memory: form.memory,
      storage: form.storage,
      replicas: form.replicas,
    }
    // shards 仅 ClickHouse 传
    if (ENGINE_META[form.engine_type].hasShards) payload.shards = form.shards
    mutation.mutate(payload)
  }

  const fieldRow = { display: 'flex', gap: 2, mb: 2 }

  return (
    <Box>
      <Typography variant="h5" sx={{ mb: 2 }}>
        创建数据库实例
      </Typography>
      <Paper sx={{ p: 3, maxWidth: 640 }}>
        {submitError && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {submitError}
          </Alert>
        )}
        <form onSubmit={handleSubmit(onSubmit)}>
          <Controller
            control={control}
            name="engine_type"
            render={({ field }) => (
              <TextField {...field} select label="引擎" fullWidth sx={{ mb: 2 }}>
                {ENGINE_LIST.map((m) => (
                  <MenuItem key={m.engine_type} value={m.engine_type}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <EngineIcon engine={m.engine_type} size={18} />
                      {m.label}
                    </Box>
                  </MenuItem>
                ))}
              </TextField>
            )}
          />

          <TextField
            label="实例名称"
            fullWidth
            sx={{ mb: 2 }}
            placeholder="小写字母开头，如 my-db-01"
            {...register('name')}
            error={!!errors.name}
            helperText={errors.name?.message}
          />

          <Box sx={fieldRow}>
            <TextField
              label="CPU"
              fullWidth
              {...register('cpu')}
              error={!!errors.cpu}
              helperText={errors.cpu?.message ?? "如 '1' / '500m'"}
            />
            <TextField
              label="内存"
              fullWidth
              {...register('memory')}
              error={!!errors.memory}
              helperText={errors.memory?.message ?? "如 '2Gi'"}
            />
          </Box>

          <Box sx={fieldRow}>
            <TextField
              label="存储"
              fullWidth
              {...register('storage')}
              error={!!errors.storage}
              helperText={errors.storage?.message ?? "如 '50Gi'"}
            />
            <TextField
              label="副本数"
              type="number"
              fullWidth
              {...register('replicas')}
              error={!!errors.replicas}
              helperText={errors.replicas?.message}
            />
            {hasShards && (
              <TextField
                label="分片数 (shards)"
                type="number"
                fullWidth
                {...register('shards')}
                error={!!errors.shards}
                helperText={errors.shards?.message ?? 'ClickHouse 专属'}
              />
            )}
          </Box>

          <Box sx={{ mt: 1, display: 'flex', gap: 1 }}>
            <Button type="submit" variant="contained" disabled={mutation.isPending}>
              {mutation.isPending ? '提交中…' : '创建'}
            </Button>
            <Button onClick={() => navigate('/databases')}>取消</Button>
          </Box>
        </form>
      </Paper>
    </Box>
  )
}
