"use client"

import React, { useState, useEffect } from "react"
import { motion } from "framer-motion"
import {
	IconX,
	IconGripVertical,
	IconPlus,
	IconLoader,
	IconSparkles,
	IconUser,
	IconDeviceFloppy
} from "@tabler/icons-react"
import ScheduleEditor from "@components/tasks/ScheduleEditor"
import { cn } from "@utils/cn"

const EditTaskModal = ({ task, onClose, onSave, allTools }) => {
	const [isSubmitting, setIsSubmitting] = useState(false)
	const [localTask, setLocalTask] = useState(task)

	useEffect(() => {
		setLocalTask(task)
	}, [task])

	const handleAddStep = () => {
		const newPlan = [
			...(localTask.plan || []),
			{ tool: "", description: "" }
		]
		setLocalTask({ ...localTask, plan: newPlan })
	}

	const handleRemoveStep = (index) => {
		setLocalTask((prev) => ({
			...prev,
			plan: prev.plan.filter((_, i) => i !== index)
		}))
	}

	const handleStepChange = (index, field, value) => {
		setLocalTask((prev) => ({
			...prev,
			plan: prev.plan.map((step, i) =>
				i === index ? { ...step, [field]: value } : step
			)
		}))
	}

	const handleFieldChange = (field, value) => {
		setLocalTask((prev) => ({ ...prev, [field]: value }))
	}

	const handleScheduleChange = (newSchedule) => {
		setLocalTask((prev) => ({ ...prev, schedule: newSchedule }))
	}

	const handleSubmit = async () => {
		setIsSubmitting(true)
		await onSave(localTask)
		setIsSubmitting(false)
	}

	return (
		<motion.div
			initial={{ opacity: 0 }}
			animate={{ opacity: 1 }}
			exit={{ opacity: 0 }}
			onClick={onClose}
			className="fixed inset-0 bg-black/60 backdrop-blur-sm flex justify-center items-center z-50 p-4"
		>
			<motion.div
				initial={{ scale: 0.9, y: 20 }}
				animate={{ scale: 1, y: 0 }}
				exit={{ scale: 0.9, y: 20 }}
				onClick={(e) => e.stopPropagation()}
				className="bg-gradient-to-br from-[var(--color-primary-surface)] to-[var(--color-primary-background)] p-6 rounded-2xl shadow-xl w-full max-w-2xl border border-[var(--color-primary-surface-elevated)] max-h-[90vh] flex flex-col"
			>
				<header className="flex justify-between items-center mb-6 flex-shrink-0">
					<h2 className="text-xl font-semibold text-white">
						Edit Task
					</h2>
					<button
						onClick={onClose}
						className="p-1 rounded-full hover:bg-[var(--color-primary-surface-elevated)]"
					>
						<IconX size={20} />
					</button>
				</header>

				<main className="flex-1 overflow-y-auto custom-scrollbar pr-2 space-y-6">
					{/* Goal & Priority */}
					<div>
						<label className="text-sm font-medium text-gray-300 mb-2 block">
							Goal & Priority
						</label>
						<div className="grid grid-cols-1 md:grid-cols-3 gap-4">
							<input
								type="text"
								value={localTask.description}
								onChange={(e) =>
									handleFieldChange(
										"description",
										e.target.value
									)
								}
								className="md:col-span-2 p-3 bg-neutral-800/50 border border-neutral-700 rounded-lg transition-colors focus:border-[var(--color-accent-blue)]"
								placeholder="Task description..."
							/>
							<select
								value={localTask.priority}
								onChange={(e) =>
									handleFieldChange(
										"priority",
										Number(e.target.value)
									)
								}
								className="p-3 bg-neutral-800/50 border border-neutral-700 rounded-lg appearance-none transition-colors focus:border-[var(--color-accent-blue)]"
							>
								<option value={0}>High Priority</option>
								<option value={1}>Medium Priority</option>
								<option value={2}>Low Priority</option>
							</select>
						</div>
					</div>

					{/* Plan Steps */}
					<div className="space-y-3">
						<label className="text-sm font-medium text-gray-300">
							Plan Steps
						</label>
						{(localTask.plan || []).map((step, index) => (
							<div
								key={index}
								className="flex items-center gap-2 p-2 bg-neutral-800/30 rounded-lg border border-neutral-700/50"
							>
								<IconGripVertical className="h-5 w-5 text-neutral-500 cursor-grab flex-shrink-0" />
								<select
									value={step.tool || ""}
									onChange={(e) =>
										handleStepChange(
											index,
											"tool",
											e.target.value
										)
									}
									className="w-1/3 p-2 bg-neutral-700 border border-neutral-600 rounded-md text-sm"
								>
									<option value="">Select tool...</option>
									{allTools.map((tool) => (
										<option
											key={tool.name}
											value={tool.name}
										>
											{tool.display_name}
										</option>
									))}
								</select>
								<input
									type="text"
									value={step.description}
									onChange={(e) =>
										handleStepChange(
											index,
											"description",
											e.target.value
										)
									}
									className="flex-grow p-2 bg-neutral-700 border border-neutral-600 rounded-md text-sm"
									placeholder="Step description..."
								/>
								<button
									onClick={() => handleRemoveStep(index)}
									className="p-2 text-red-400 hover:bg-red-500/10 rounded-full flex-shrink-0"
								>
									<IconX size={16} />
								</button>
							</div>
						))}
						<button
							onClick={handleAddStep}
							className="flex items-center gap-1.5 text-xs py-1.5 px-3 rounded-full bg-neutral-700 hover:bg-neutral-600"
						>
							<IconPlus size={14} /> Add Step
						</button>
					</div>

					{/* Assignee */}
					<div>
						<label className="block text-sm font-medium text-gray-300 mb-2">
							Assignee
						</label>
						<div className="flex gap-1 p-1 bg-neutral-800/50 rounded-lg border border-neutral-700 w-full">
							<button
								onClick={() =>
									handleFieldChange("assignee", "ai")
								}
								className={cn(
									"flex-1 flex items-center justify-center gap-2 py-1.5 rounded-md text-sm transition-colors",
									localTask.assignee === "ai"
										? "bg-blue-600 text-white"
										: "hover:bg-neutral-700"
								)}
							>
								<IconSparkles size={16} /> Sentient
							</button>
							<button
								onClick={() =>
									handleFieldChange("assignee", "user")
								}
								className={cn(
									"flex-1 flex items-center justify-center gap-2 py-1.5 rounded-md text-sm transition-colors",
									localTask.assignee === "user"
										? "bg-blue-600 text-white"
										: "hover:bg-neutral-700"
								)}
							>
								<IconUser size={16} /> Me
							</button>
						</div>
					</div>

					{/* Schedule */}
					<div>
						<label className="text-sm font-medium text-gray-300 mb-2 block">
							Schedule
						</label>
						<ScheduleEditor
							schedule={
								localTask.schedule || {
									type: "once",
									run_at: null
								}
							}
							setSchedule={handleScheduleChange}
						/>
					</div>
				</main>

				<footer className="mt-6 pt-4 border-t border-[var(--color-primary-surface-elevated)] flex justify-end gap-4 flex-shrink-0">
					<button
						type="button"
						onClick={onClose}
						className="py-2.5 px-6 rounded-lg bg-neutral-700 hover:bg-neutral-600 text-sm transition-colors"
					>
						Cancel
					</button>
					<button
						onClick={handleSubmit}
						disabled={isSubmitting}
						className="py-2.5 px-6 rounded-lg bg-blue-600 hover:bg-blue-500 text-sm flex items-center gap-2 disabled:opacity-50 transition-colors"
					>
						{isSubmitting && (
							<IconLoader size={16} className="animate-spin" />
						)}
						{isSubmitting ? (
							"Saving..."
						) : (
							<>
								<IconDeviceFloppy size={16} /> Save Changes
							</>
						)}
					</button>
				</footer>
			</motion.div>
		</motion.div>
	)
}

export default EditTaskModal
