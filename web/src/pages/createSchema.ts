import { z } from 'zod'

// 前端校验规则与后端 Pydantic (app/models/specs.py) 严格对齐
const NAME_RE = /^[a-z][a-z0-9-]*$/
const CPU_RE = /^(\d+(\.\d+)?|\d+m)$/
const QTY_RE = /^\d+(Gi|Mi)$/

export const createDatabaseSchema = z.object({
  name: z
    .string()
    .min(1, '必填')
    .max(63, '不超过 63 字符')
    .regex(NAME_RE, '小写字母开头，仅含小写字母/数字/连字符'),
  engine_type: z.enum([
    'mysql',
    'postgresql',
    'mongodb',
    'clickhouse',
    'redis',
    'elasticsearch',
    'kafka',
  ]),
  cpu: z.string().regex(CPU_RE, "格式如 '1' / '0.5' / '500m'"),
  memory: z.string().regex(QTY_RE, "用二进制单位，如 '2Gi' / '512Mi'"),
  storage: z.string().regex(QTY_RE, "用二进制单位，如 '50Gi'"),
  replicas: z.coerce.number().int().min(1, '至少 1'),
  shards: z.coerce.number().int().min(1, '至少 1').optional(),
})

export type CreateDatabaseForm = z.infer<typeof createDatabaseSchema>
