# Ordinal measurement comparisons use an established WLSMV implementation.
suppressPackageStartupMessages(library(lavaan))
suppressPackageStartupMessages(library(semTools))
suppressPackageStartupMessages(library(jsonlite))

args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 2L) stop("Expected request JSON and aggregate result JSON paths.")
request <- fromJSON(args[1], simplifyVector = TRUE)
dat <- read.csv(request$data_csv, check.names = FALSE)
dat$Country <- factor(dat$Country, levels = request$countries)
if (anyNA(dat)) stop("Ordinal inference requires the audited complete sample.")

records <- list()
parameters <- list()
warnings_out <- list()
comparisons <- list()
decisions <- list()

fit_model <- function(model, items, data, group, equal, label, construct) {
  captured <- character()
  fit <- withCallingHandlers(
    measEq.syntax(configural.model = model, data = data, ordered = items,
                  group = group, group.equal = equal,
                  parameterization = "theta", ID.fac = "std.lv",
                  ID.cat = "Wu.Estabrook.2016", estimator = "WLSMV",
                  return.fit = TRUE),
    warning = function(w) {
      captured <<- c(captured, conditionMessage(w))
      invokeRestart("muffleWarning")
    }
  )
  converged <- lavInspect(fit, "converged")
  if (!converged) stop(paste("Ordinal model failed to converge:", construct, label))
  corr <- lavInspect(fit, "cor.lv")
  if (!is.list(corr)) corr <- list(corr)
  theta <- lavInspect(fit, "theta")
  if (!is.list(theta)) theta <- list(theta)
  pe <- parameterEstimates(fit, standardized = TRUE)
  if (!"group" %in% names(pe)) pe$group <- 1L
  loadings <- pe$std.all[pe$op == "=~"]
  proper <- all(vapply(corr, function(x) min(eigen(x, symmetric=TRUE)$values) > 1e-8,
                       logical(1))) &&
            all(vapply(theta, function(x) min(diag(x)) > 0, logical(1))) &&
            all(is.finite(loadings)) && all(abs(loadings) < 1) &&
            all(is.finite(pe$se))
  metrics <- fitMeasures(fit, c("chisq.scaled", "df.scaled", "pvalue.scaled",
                               "cfi.scaled", "tli.scaled", "rmsea.scaled",
                               "rmsea.ci.lower.scaled", "rmsea.ci.upper.scaled",
                               "srmr", "cfi.robust", "rmsea.robust"))
  pass <- proper && all(is.finite(metrics[c("cfi.scaled", "rmsea.scaled", "srmr")])) &&
          metrics["cfi.scaled"] >= request$minimum_cfi &&
          metrics["rmsea.scaled"] <= request$maximum_rmsea &&
          metrics["srmr"] <= request$maximum_srmr
  records[[length(records) + 1L]] <<- c(list(construct=construct, model=label,
      converged=converged, proper=proper, passes_followup_screen=as.logical(pass)),
      as.list(metrics))
  pe$construct <- construct
  pe$model <- label
  parameters[[length(parameters) + 1L]] <<- pe[, c("construct", "model", "lhs", "op", "rhs",
                                                 "group", "est", "se", "std.all")]
  if (length(captured)) {
    for (w in unique(captured)) warnings_out[[length(warnings_out)+1L]] <<-
      list(construct=construct, model=label, message=w)
  }
  list(fit=fit, pass=pass, proper=proper)
}

for (construct in names(request$models)) {
  spec <- request$models[[construct]]
  items <- unlist(spec$items, use.names=FALSE)
  if (!all(items %in% names(dat))) stop("Required ordinal model items are missing.")
  supports <- lapply(request$countries, function(country)
    lapply(dat[dat$Country==country, items, drop=FALSE], function(x) sort(unique(x))))
  if (!all(vapply(supports, function(s) all(vapply(s, function(x)
      identical(as.integer(x), 1:5), logical(1))), logical(1)))) {
    decisions[[construct]] <- list(status="blocked_category_support",
      reason="At least one item lacks a category within a country; no category collapsing.")
    next
  }
  country_pass <- logical()
  for (country in request$countries) {
    result <- fit_model(spec$syntax, items, dat[dat$Country==country, ], NULL, "",
                        paste0("configural_", country), construct)
    country_pass <- c(country_pass, result$pass)
  }
  previous <- fit_model(spec$syntax, items, dat, "Country", "", "configural", construct)
  if (!all(country_pass) || !previous$pass) {
    decisions[[construct]] <- list(status="blocked_configural_screen",
      reason="At least one country or multigroup configural model fails the declared fit/admissibility screen. Equality constraints are not interpreted.")
    next
  }
  equal <- character()
  for (constraint in c("thresholds", "loadings", "intercepts")) {
    equal <- c(equal, constraint)
    current <- fit_model(spec$syntax, items, dat, "Country", equal,
                         paste(equal, collapse="_"), construct)
    if (!current$proper) {
      decisions[[construct]] <- list(status="blocked_inadmissible_constraints", at=constraint)
      break
    }
    difference <- lavTestLRT(previous$fit, current$fit, method="satorra.2000")
    p <- difference[2, "Pr(>Chisq)"]
    comparisons[[length(comparisons)+1L]] <- list(
      construct=construct, added_constraint=constraint,
      method="WLSMV scaled-shifted Satorra-2000 nested comparison",
      chi_square_difference=unname(difference[2, "Chisq diff"]),
      df_difference=unname(difference[2, "Df diff"]), p_value=unname(p))
    if (!is.finite(p)) stop("Nonfinite robust nested-model comparison.")
    if (p < request$alpha) {
      decisions[[construct]] <- list(status="equality_not_supported", at=constraint,
                                     reason="Sequential robust equality test rejected; no partial-invariance search.")
      break
    }
    previous <- current
    decisions[[construct]] <- list(status="constraints_not_rejected", through=constraint,
      reason="Non-rejection is not proof of invariance, translation equivalence, or adequate power.")
  }
}

result <- list(estimator="WLSMV", parameterization="theta",
  identification="semTools Wu.Estabrook.2016 with std.lv",
  versions=list(R=as.character(getRversion()), lavaan=as.character(packageVersion("lavaan")),
                semTools=as.character(packageVersion("semTools"))),
  models=records, parameters=if(length(parameters)) do.call(rbind, parameters) else list(),
  warnings=warnings_out, comparisons=comparisons, decisions=decisions)
write_json(result, args[2], auto_unbox=TRUE, pretty=TRUE, digits=16, na="null")
